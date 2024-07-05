"""
app = Flask(__name__)


@app.route('/estimatee')
def estimatee():
    return render_template('index.html')

@app.route('/estimate', methods=['POST'])
def estimate():
    try:
        
        bedrooms = float(request.form.get('bedrooms', 0))
        bathrooms = float(request.form.get('bathrooms', 0))
        sqft_lot = float(request.form.get('sqft_lot', 0))
        sqft_living = float(request.form.get('sqft_living', 0))

        
        prediction = ai_moudel.predict({
            'bedrooms': bedrooms,
            'bathrooms': bathrooms,
            'sqft_lot': sqft_lot,
            'sqft_living': sqft_living
        })

        
        return render_template('index.html', estimated_price=prediction)

    except Exception as e:
        
        return render_template('index.html', error_message=str(e))
"""