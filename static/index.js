// Login page
function myFunction() {
  var x = document.getElementById("password");
  if (x.type === "password") {
    x.type = "text";
  } else {
    x.type = "password";
  }
}
// Set a timeout to hide the flash message after 2 seconds
setTimeout(function () {
  var flashMessage = document.getElementById("flash-message");
  if (flashMessage) {
    flashMessage.style.display = "none";
  }
}, 2000);
// Adding listings
document.addEventListener("DOMContentLoaded", () => {
  const sellButton = document.getElementById("sell-button");
  const rentButton = document.getElementById("rent-button");

  sellButton.addEventListener("click", () => {
    sellButton.classList.add("active");
    sellButton.classList.remove("inactive");
    rentButton.classList.add("inactive");
    rentButton.classList.remove("active");
    document.getElementById("action").value = "sell";
  });

  rentButton.addEventListener("click", () => {
    rentButton.classList.add("active");
    rentButton.classList.remove("inactive");
    sellButton.classList.add("inactive");
    sellButton.classList.remove("active");
    document.getElementById("action").value = "rent";
  });

  document.getElementById("image").addEventListener("change", function (event) {
    const files = event.target.files;
    const container = document.getElementById("image-preview-container");

    container.innerHTML = "";

    if (files.length > 0) {
      Array.from(files).forEach((file) => {
        const reader = new FileReader();
        reader.onload = function (e) {
          const img = document.createElement("img");
          img.src = e.target.result;
          img.classList.add("w-full", "h-auto", "object-cover", "rounded-lg");
          container.appendChild(img);
        };
        reader.readAsDataURL(file);
      });

      document.getElementById("no-image").classList.add("hidden");
    } else {
      if (container.children.length === 0) {
        document.getElementById("no-image").classList.remove("hidden");
      }
    }
  });
});

// Navbar
document.getElementById("nav-toggle").addEventListener("click", function () {
  var navMenu = document.getElementById("nav-menu");
  if (navMenu.classList.contains("hidden")) {
    navMenu.classList.remove("hidden");
    navMenu.classList.add("flex");
  } else {
    navMenu.classList.add("hidden");
    navMenu.classList.remove("flex");
  }
});

// Home heart color
document.addEventListener("DOMContentLoaded", () => {
  // Set the initial state of the heart icons based on the saved status
  document.querySelectorAll(".heart-icon").forEach((icon) => {
    const listingId = icon.getAttribute("data-listing-id");
    fetch(`/user/is_listing_saved/${listingId}`)
      .then((response) => response.json())
      .then((data) => {
        if (data.saved) {
          icon.src = "/static/images/heart_active.png";
          icon.setAttribute("data-state", "active");
        } else {
          icon.src = "/static/images/heart_inactive.png";
          icon.setAttribute("data-state", "inactive");
        }
      });

    // Add event listener to toggle the heart icon state
    icon.addEventListener("click", (event) => {
      const state = icon.getAttribute("data-state");
      toggleHeart(event, listingId, state);
    });
  });
});

function toggleHeart(event, listingId, state) {
  const icon = event.target;

  if (state === "inactive") {
    // Save the listing
    fetch(`/user/save_listing/${listingId}`, { method: "POST" })
      .then((response) => response.json())
      .then((data) => {
        if (data.success) {
          icon.src = "/static/images/heart_active.png";
          icon.setAttribute("data-state", "active");
        } else {
          alert(data.message); // Display the error message
        }
      });
  } else {
    // Remove the listing
    fetch(`/user/remove_listing/${listingId}`, { method: "POST" })
      .then((response) => response.json())
      .then((data) => {
        if (data.success) {
          icon.src = "/static/images/heart_inactive.png";
          icon.setAttribute("data-state", "inactive");
        } else {
          alert(data.message); // Display the error message
        }
      });
  }
}

// Admin inbox
document.getElementById("nav-toggle").addEventListener("click", function () {
  var navMenu = document.getElementById("nav-menu");
  if (navMenu.classList.contains("hidden")) {
    navMenu.classList.remove("hidden");
    navMenu.classList.add("flex");
  } else {
    navMenu.classList.add("hidden");
    navMenu.classList.remove("flex");
  }
});

// FAQ page
document.querySelectorAll(".question").forEach((question) => {
  question.addEventListener("click", () => {
    const answer = question.nextElementSibling;
    answer.classList.toggle("hidden");
  });
});

//product page image function
document.addEventListener("DOMContentLoaded", () => {
  const thumbnails = document.querySelectorAll(".thumbnail");
  const mainImage = document.getElementById("main-image");

  thumbnails.forEach((thumbnail) => {
    thumbnail.addEventListener("click", function () {
      const newSrc = this.src;
      mainImage.src = newSrc;
    });
  });
});
