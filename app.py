from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify, Blueprint
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message
from flask_migrate import Migrate
from werkzeug.utils import secure_filename
import pandas as pd
import os
import random
import string
import pickle
from sqlalchemy import or_




app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'  
app.config['UPLOAD_FOLDER'] = 'static/uploads'

# Mail configuration
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'housy.ewa@gmail.com'
app.config['MAIL_PASSWORD'] = 'pzpx bgum fgbc mhaj'  

mail = Mail(app)
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Blueprints
admin_bp = Blueprint('admin', __name__, url_prefix='/admin')
user_bp = Blueprint('user', __name__, url_prefix='/user')

# Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fullname = db.Column(db.String(120), nullable=False)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(20), nullable=True)
    profile_picture = db.Column(db.String(120), nullable=False)
    saved_listings = db.relationship('SavedListing', backref='user', lazy=True)
    reset_code = db.Column(db.String(6), nullable=True)

class Listing(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    bedrooms = db.Column(db.Integer)
    bathrooms = db.Column(db.Integer)
    square_footage = db.Column(db.Integer)
    price = db.Column(db.Float)
    city = db.Column(db.String(100))
    description = db.Column(db.Text)
    action = db.Column(db.String(10))
    images = db.relationship('ListingImage', backref='listing', cascade='all, delete-orphan', lazy=True)

class ListingImage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(100))
    listing_id = db.Column(db.Integer, db.ForeignKey('listing.id'), nullable=False)

class SavedListing(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    listing_id = db.Column(db.Integer, db.ForeignKey('listing.id'), nullable=False)

class MessageModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), nullable=False)
    message = db.Column(db.Text, nullable=False)


with app.app_context():
    db.create_all()

# Routes for admin blueprint
@admin_bp.route('/')
def admin_home():
    if session.get('role') != 'admin':
        return redirect(url_for('user.user_home'))
    listings = Listing.query.order_by(Listing.id.desc()).all()
    return render_template('admin_listing_page.html', listings=listings)

@admin_bp.route('/profile')
def admin_profile():
    if session.get('role') != 'admin':
        return redirect(url_for('user.user_home'))
    return redirect(url_for('admin.admin_home'))

@admin_bp.route('/add_listing', methods=['GET', 'POST'])
def add_listing():
    if request.method == 'POST':
        images = request.files.getlist('images')
        if images:
            new_listing = Listing(
                bedrooms=request.form['bedrooms'],
                bathrooms=request.form['bathrooms'],
                square_footage=request.form['square_footage'],
                price=request.form['price'],
                city=request.form['city'],
                description=request.form['description'],
                action=request.form['action']
            )

            db.session.add(new_listing)
            db.session.commit()

            for image in images:
                if image.filename != '':
                    filename = secure_filename(image.filename)
                    image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    image.save(image_path)
                    new_image = ListingImage(filename=filename, listing_id=new_listing.id)
                    db.session.add(new_image)

            db.session.commit()
            return redirect(url_for('admin.admin_home'))

    return render_template('adding_listes_page.html')

@admin_bp.route('/edit_listing/<int:listing_id>', methods=['GET', 'POST'])
def edit_listing(listing_id):
    listing = Listing.query.get_or_404(listing_id)

    if request.method == 'POST':
        listing.bedrooms = request.form['bedrooms']
        listing.bathrooms = request.form['bathrooms']
        listing.square_footage = request.form['square_footage']
        listing.price = request.form['price']
        listing.city = request.form['city']
        listing.description = request.form['description']
        listing.action = request.form['action']

        
        for image in listing.images:
            file = request.files.get(f'image-{image.id}')
            if file and file.filename:
                filename = secure_filename(file.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                image.filename = filename

        db.session.commit()
        return redirect(url_for('admin.admin_home'))

    return render_template('edit_listing.html', listing=listing)

@admin_bp.route('/delete_listing/<int:listing_id>', methods=['POST'])
def delete_listing(listing_id):
    listing = Listing.query.get_or_404(listing_id)
    try:
        db.session.delete(listing)
        db.session.commit()
        flash('Listing deleted successfully!')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting listing: {str(e)}')
    return redirect(url_for('admin.admin_home'))

@admin_bp.route('/inbox')
def inbox():
    messages = MessageModel.query.all()
    return render_template('admin_inBox.html', messages=messages)

# Routes for user blueprint
@user_bp.route('/home')
def user_home():
    listings = Listing.query.order_by(Listing.id.desc()).limit(4).all()

    if 'role' in session and session['role'] == 'admin':
        user_profile_picture = None
    elif 'username' in session:
        user = User.query.filter_by(username=session['username']).first()
        user_profile_picture = user.profile_picture if user.profile_picture else 'static/images/admin.png'
    else:
        user_profile_picture = 'static/images/admin.png'

    return render_template('home2.html', listings=listings, user_profile_picture=user_profile_picture)


@user_bp.route('/save_listing/<int:listing_id>', methods=['POST'])
def save_listing(listing_id):
    if 'username' not in session:
        return jsonify({'success': False, 'message': 'User not logged in'}), 401

    user = User.query.filter_by(username=session['username']).first()
    if user:
        saved_listing = SavedListing(user_id=user.id, listing_id=listing_id)
        db.session.add(saved_listing)
        db.session.commit()
        return jsonify({'success': True}), 200
    return jsonify({'success': False}), 400

@user_bp.route('/remove_listing/<int:listing_id>', methods=['POST'])
def remove_listing(listing_id):
    if 'username' not in session:
        return jsonify({'success': False, 'message': 'User not logged in'}), 401

    user = User.query.filter_by(username=session['username']).first()
    if user:
        saved_listing = SavedListing.query.filter_by(user_id=user.id, listing_id=listing_id).first()
        if saved_listing:
            db.session.delete(saved_listing)
            db.session.commit()
            return jsonify({'success': True}), 200
    return jsonify({'success': False}), 400

@user_bp.route('/profile', methods=['GET'])
def user_profile():
    if 'username' in session:
        user = User.query.filter_by(username=session['username']).first()
        if user:
            user_full_name = user.fullname
            user_email = user.email
            user_profile_picture = user.profile_picture
            saved_listings = SavedListing.query.filter_by(user_id=user.id).all()
            listings = [Listing.query.get(saved.listing_id) for saved in saved_listings]
            return render_template('user_saving_page.html', user_full_name=user_full_name, user_email=user_email, user_profile_picture=user_profile_picture ,listings=listings)
        else:
            flash('User not found')
            return redirect(url_for('user.user_home'))
    else:
        flash('You need to log in to view saved listings')
        return redirect(url_for('user.login'))

@user_bp.route('/is_listing_saved/<int:listing_id>', methods=['GET'])
def is_listing_saved(listing_id):
    if 'username' not in session:
        return jsonify({'saved': False})

    user = User.query.filter_by(username=session['username']).first()
    if user:
        saved_listing = SavedListing.query.filter_by(user_id=user.id, listing_id=listing_id).first()
        if saved_listing:
            return jsonify({'saved': True})
    return jsonify({'saved': False})

@user_bp.route('/saved_listings', methods=['GET'])
def saved_listings():
    if 'username' not in session:
        flash('You need to log in to view saved listings')
        return redirect(url_for('user.login'))

    user = User.query.filter_by(username=session['username']).first()
    if user:
        user_full_name = user.fullname
        user_email = user.email
        user_profile_picture = user.profile_picture
        saved_listings = SavedListing.query.filter_by(user_id=user.id).all()
        listings = [Listing.query.get(saved.listing_id) for saved in saved_listings]
        return render_template('user_saving_page.html', listings=listings , user_full_name=user_full_name, user_email=user_email, user_profile_picture=user_profile_picture)
    return redirect(url_for('user.user_home'))

@user_bp.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form['email']
        user = User.query.filter_by(email=email).first()
        if user:
            reset_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
            user.reset_code = reset_code
            db.session.commit()
            msg = Message(sender='housy.ewa@gmail.com', recipients=[email])
            msg.subject = 'Password Reset Request'
            msg.body = f'Your password reset code is {reset_code}'
            mail.send(msg)
            flash('A reset code has been sent to your email.')
            return redirect(url_for('user.verify_code'))
        else:
            flash('Email not found.')
    return render_template('resetPassword.html')

@user_bp.route('/verify_code', methods=['GET', 'POST'])
def verify_code():
    if request.method == 'POST':
        email = request.form['email']
        reset_code = request.form['reset_code']
        user = User.query.filter_by(email=email, reset_code=reset_code).first()
        if user:
            new_password = request.form['new_password']
            confirm_password = request.form['confirm_password']
            if new_password == confirm_password:
                user.password = new_password
                user.reset_code = None
                db.session.commit()
                flash('Your password has been reset. You can now log in.')
                return redirect(url_for('login'))  
            else:
                flash('Passwords do not match.')
        else:
            flash('Invalid reset code.')
    return render_template('verify_code.html')


app.register_blueprint(admin_bp)
app.register_blueprint(user_bp)

# Registration and login
@app.route('/registration', methods=['GET', 'POST'])
def registration():
    if 'username' in session:
        return redirect(url_for('user.user_home'))

    if request.method == 'POST':
        fullname = request.form['fullname']
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        phone = request.form['phone']

        if password != confirm_password:
            flash('Passwords do not match!')
            return redirect(url_for('registration'))

        # Check username if exisit
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('Username already taken. Please choose a different username.')
            return redirect(url_for('registration'))
        
        # Check email if exist
        existing_email = User.query.filter_by(email=email).first()
        if existing_email:
            flash('Email already registered. Please use a different email address or log in.')
            return redirect(url_for('registration'))

        # profile picture
        profile_picture = request.files['profile_picture']
        if profile_picture:
            filename = secure_filename(profile_picture.filename)
            profile_picture.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        else:
            filename = 'static/images/default_user.png'  

        new_user = User(fullname=fullname, username=username, email=email, password=password, phone=phone, profile_picture=filename)
        db.session.add(new_user)
        db.session.commit()

        flash('Registration successful! Please log in.')
        return redirect(url_for('login'))
    
    return render_template('registration.html')

model_file = open('model.pkl', 'rb')
model = pickle.load(model_file)
model_file.close()

@app.route('/estimatee')
def estimatee():
    return render_template('index.html')

@app.route('/estimate', methods=['POST'])
def estimate():
    try:
        
        bedrooms = float(request.form['bedrooms'])
        bathrooms = float(request.form['bathrooms'])
        sqft_lot = float(request.form['sqft_lot'])
        sqft_living = float(request.form['sqft_living'])

        input_data = pd.DataFrame({
            'bedrooms': [bedrooms],
            'bathrooms': [bathrooms],
            'sqft_living': [sqft_living],
            'sqft_lot': [sqft_lot]
            
        })
        print(input_data)


        prediction = model.predict(input_data)

        
        return render_template('index.html', estimated_price=prediction[0])

    except Exception as e:
        
        return render_template('index.html', error_message=str(e))



@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'username' in session:
        return redirect(url_for('user.user_home'))

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if username == 'admin' and password == 'admin':
            session['username'] = username
            session['role'] = 'admin'
            return redirect(url_for('user.user_home'))

        user = User.query.filter_by(username=username, password=password).first()
        if user:
            session['username'] = user.username
            session['role'] = 'user'
            flash('Login successful!')
            return redirect(url_for('user.user_home'))
        else:
            flash('Invalid credentials, please try again.')

    return render_template('login.html')



@app.route('/logout')
def logout():
    session.pop('username', None)
    session.pop('role', None)
    flash('You have been logged out.')
    return redirect(url_for('login'))

# Other routes
@app.route('/')
def home1():
    listings = Listing.query.order_by(Listing.id.desc()).limit(4).all()
    
    if 'username' in session:
        user = User.query.filter_by(username=session['username']).first()
        user_profile_picture = user.profile_picture if user and user.profile_picture else 'static/images/default_user.png'
        return render_template('home.html', username=session['username'], listings=listings, user_profile_picture=user_profile_picture)
    else:
        user_profile_picture = 'static/images/default_user.png'
        return render_template('home.html', listings=listings, user_profile_picture=user_profile_picture)


@app.route('/home')
def home():
    listings = Listing.query.order_by(Listing.id.desc()).limit(4).all()
    return render_template('home2.html', listings=listings)

@app.route('/about')
def about():
    if 'role' in session and session['role'] == 'admin':
        user_profile_picture = None
    elif 'username' in session:
        user = User.query.filter_by(username=session['username']).first()
        user_profile_picture = user.profile_picture if user.profile_picture else 'static/images/admin_logo.png'
    else:
        user_profile_picture = 'static/images/admin_logo.png'

    return render_template('about us.html', user_profile_picture=user_profile_picture)

@app.route('/product/<int:listing_id>')
def product(listing_id):
    if 'role' in session and session['role'] == 'admin':
        user_profile_picture = None
    elif 'username' in session:
        user = User.query.filter_by(username=session['username']).first()
        user_profile_picture = user.profile_picture if user.profile_picture else 'static/images/admin_logo.png'
    else:
        user_profile_picture = 'static/images/admin_logo.png'
    listing = Listing.query.get_or_404(listing_id)
    images = ListingImage.query.filter_by(listing_id=listing_id).all()
    return render_template('product.html', listing=listing, images=images ,user_profile_picture=user_profile_picture)


@app.route('/rent', methods=['GET', 'POST'])
def rent():
    filter_conditions = [Listing.action == 'rent']

    if request.method == 'POST':
        bedrooms = request.form.get('bedrooms')
        bathrooms = request.form.get('bathrooms')
        city = request.form.get('city')
        price = request.form.get('price')

        if bedrooms:
            filter_conditions.append(Listing.bedrooms <= int(bedrooms))
        if bathrooms:
            filter_conditions.append(Listing.bathrooms <= int(bathrooms))
        if city:
            filter_conditions.append(Listing.city.ilike(f"%{city}%"))
        if price:
            filter_conditions.append(Listing.price <= float(price))

    listings = Listing.query.filter(*filter_conditions).all()

    if 'role' in session and session['role'] == 'admin':
        user_profile_picture = None
    elif 'username' in session:
        user = User.query.filter_by(username=session['username']).first()
        user_profile_picture = user.profile_picture if user and user.profile_picture else 'static/images/admin_logo.png'
    else:
        user_profile_picture = 'static/images/admin_logo.png'

    return render_template('rent.html', listings=listings, user_profile_picture=user_profile_picture)


@app.route('/sell', methods=['GET', 'POST'])
def sell():
    filter_conditions = [Listing.action == 'sell']

    if request.method == 'POST':
        bedrooms = request.form.get('bedrooms')
        bathrooms = request.form.get('bathrooms')
        city = request.form.get('city')
        price = request.form.get('price')

        if bedrooms:
            filter_conditions.append(Listing.bedrooms <= int(bedrooms))
        if bathrooms:
            filter_conditions.append(Listing.bathrooms <= int(bathrooms))
        if city:
            filter_conditions.append(Listing.city.ilike(f"%{city}%"))
        if price:
            filter_conditions.append(Listing.price <= float(price))

    listings = Listing.query.filter(*filter_conditions).all()

    if 'role' in session and session['role'] == 'admin':
        user_profile_picture = None
    elif 'username' in session:
        user = User.query.filter_by(username=session['username']).first()
        user_profile_picture = user.profile_picture if user and user.profile_picture else 'static/images/admin_logo.png'
    else:
        user_profile_picture = 'static/images/admin_logo.png'

    return render_template('sell.html', listings=listings, user_profile_picture=user_profile_picture)





@app.route('/faq')
def faq():
    if 'username' in session:
        user = User.query.filter_by(username=session['username']).first()
        if user:
            user_full_name = user.fullname
            user_email = user.email
            user_profile_picture = user.profile_picture
        else:
            user_full_name = 'Guest User'
            user_email = 'guest@example.com'
            user_profile_picture = '/static/images/admin_logo.png'  
    else:
        user_full_name = 'Guest User'
        user_email = 'guest@example.com'
        user_profile_picture = '/static/images/admin_logo.png'

    return render_template('FAQ.html', user_full_name=user_full_name, user_email=user_email, user_profile_picture=user_profile_picture)


@app.route('/contact_us')
def contact_us():
    if 'role' in session and session['role'] == 'admin':
        user_profile_picture = None
    elif 'username' in session:
        user = User.query.filter_by(username=session['username']).first()
        user_profile_picture = user.profile_picture if user.profile_picture else 'static/images/admin_logo.png'
    else:
        user_profile_picture = 'static/images/admin_logo.png'

    return render_template('contact us.html', user_profile_picture=user_profile_picture)


@app.errorhandler(404)
def page_not_found(e):
    return render_template('Error page.html'), 404

@app.route('/contactsupport', methods=['GET', 'POST'])
def contactsupport():
    if 'username' in session:
        user = User.query.filter_by(username=session['username']).first()
        if user:
            user_full_name = user.fullname
            user_email = user.email
            user_profile_picture = user.profile_picture
    else:
        user_full_name = 'Guest User'
        user_email = 'guest@example.com'

    if request.method == 'POST':
        return redirect(url_for('send_message'))
    return render_template('contactsupport.html', user_full_name=user_full_name, user_email=user_email , user_profile_picture=user_profile_picture)

@app.route('/send_message', methods=['POST'])
def send_message():
    email = request.form['email']
    message_text = request.form['message']
    new_message = MessageModel(email=email, message=message_text)
    db.session.add(new_message)
    db.session.commit()
    flash('Message sent successfully!')
    return redirect(url_for('contactsupport'))

@app.route('/inbox')
def inbox():
    messages = MessageModel.query.all()
    return render_template('admin_inBox.html', messages=messages)

@app.route('/setting', methods=['GET', 'POST'])
def setting():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        phone = request.form['phone']
        profile_picture = request.files['profile_picture']

        user = User.query.filter_by(username=session['username']).first()
        if user:
            if profile_picture:
                filename = secure_filename(profile_picture.filename)
                profile_picture.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                user.profile_picture = filename
            user.username = username
            user.email = email
            user.phone = phone
            db.session.commit()
            session['username'] = username
            flash('Settings updated successfully!')
        else:
            flash('User not found!')

        return redirect(url_for('setting'))

    if 'username' in session:
        user = User.query.filter_by(username=session['username']).first()
        return render_template('Setting.html', user=user)
    else:
        flash('You need to be logged in to view this page.')
        return redirect(url_for('login'))




if __name__ == '__main__':
    with app.app_context():
        
        db.create_all()
    app.run(debug=True)
