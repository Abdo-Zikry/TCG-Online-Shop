/*! Start Bootstrap - Shop Homepage v5.0.6 (https://startbootstrap.com/template/shop-homepage)
* Copyright 2013-2023 Start Bootstrap
* Licensed under MIT (https://github.com/StartBootstrap/startbootstrap-shop-homepage/blob/master/LICENSE)*/

// This file is intentionally blank
// Use this file to add JavaScript to your project
document.addEventListener('DOMContentLoaded', function() {
    // Function to validate password match for both register and settings forms
    function validatePasswordMatch(formId, passwordId, confirmPasswordId) {
        var form = document.getElementById(formId);

        if (form) {
            form.addEventListener('submit', function(event) {
                var password = document.getElementById(passwordId).value;
                var confirmPassword = document.getElementById(confirmPasswordId).value;

                if (password !== confirmPassword) {
                    alert('Passwords do not match.');
                    event.preventDefault(); // Prevent submission
                }
            });
        }
    }

    // Validate password match for both registration form and settings form
    validatePasswordMatch('registerForm', 'password', 'confirm_password');
    validatePasswordMatch('settingsForm', 'new_password', 'confirm_new_password');
});

// Function to retrieve the CSRF token from the meta tag
function getCSRFToken() {
    return document.querySelector('meta[name="csrf-token"]').getAttribute('content');
}

// JavaScript function to add a product to the cart
function addToCart(productId, maxStock) {
    fetch('/add_to_cart', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCSRFToken(),
        },
        body: JSON.stringify({ 
            'product_id': productId,
            'max_stock': maxStock
         })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Update the cart count dynamically
            document.getElementById('cart-count').textContent = data.cart_count;
        } else {
            // Display a message if a problem
            alert(data.message);
        }
    })
    .catch(error => {
        console.error('Error:', error);
    });
}

// JavaScript function to adjust the cart quantity
function adjustCartQuantity(productId, change) {
    // Get the input field for the product quantity
    const quantityInput = document.getElementById('quantity-' + productId);
    let newQuantity = parseInt(quantityInput.value) + change;
    const maxStock = parseInt(quantityInput.max);

    // Ensure the quantity doesn't go below 0 or above maximum
    if (newQuantity < 0) {
        newQuantity = 0;
    }
    if (newQuantity > maxStock) {
        newQuantity = maxStock;
    }

    // Update the input field with the new quantity
    quantityInput.value = newQuantity;

    // Send an AJAX request to update the cart on the server
    fetch('/update_cart', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCSRFToken(),
        },
        body: JSON.stringify({
            'product_id': productId,
            'new_quantity': newQuantity
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Update the cart count displayed on the page
            document.getElementById('cart-count').textContent = data.cart_count;
        } else {
            alert('Failed to update cart');
        }
    })
    .catch(error => {
        console.error('Error:', error);
    });
}

// JavaScript function to update the cart quantity manually
function manualCartUpdate(productId) {
    // Obtain the new quantity entered
    const quantityInput = document.getElementById('quantity-' + productId);
    const newQuantity = parseInt(quantityInput.value);
    const maxStock = parseInt(quantityInput.max);

    // Ensure the new quantity is not less than 0 and does not exceed max stock
    if (newQuantity < 0) {
        alert('Quantity cannot be less than 0. Update was discarded.');
        quantityInput.value = 0;
        return;
    }
    if (newQuantity > maxStock) {
        alert(`Maximum stock available is ${maxStock}. Update was discarded.`);
        quantityInput.value = maxStock;
        return;
    }

    fetch('/update_cart', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCSRFToken(),
        },
        body: JSON.stringify({ 'product_id': productId, 'new_quantity': newQuantity })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Update the cart icon count
            document.getElementById('cart-count').textContent = data.cart_count;
            quantityInput.setAttribute('data-original-quantity', newQuantity);
        } else {
            alert('Failed to update cart');
        }
    })
    .catch(error => {
        console.error('Error:', error);
    });
}

// Function to check if the product quantity input has changed without update
function checkInputChange(productId) {
    // Retrieve the new quantity input
    const quantityInput = document.getElementById('quantity-' + productId);
    const originalQuantity = parseInt(quantityInput.getAttribute('data-original-quantity'));
    const currentQuantity = parseInt(quantityInput.value);

    if (currentQuantity !== originalQuantity) {
        alert("Changes were not recorded, you have to click enter.");
    }
}

// Function to handle updating the cart when the Enter key is pressed
function checkEnterKey(event, productId) {
    if (event.key === 'Enter') {  
        manualCartUpdate(productId);
    }
}

// Function to save the cart when the page is closed
window.addEventListener('unload', function () {
    // Send a request to the backend to save the cart
    if (isLoggedIn) {
    navigator.sendBeacon('/save_cart');
    }
});

// Function to dynamically update the navbar label when the collapse is shown/hidden
document.addEventListener('DOMContentLoaded', function () {
    // Get elements
    const navbarLabel = document.getElementById('navbarLabel');
    const shopNavbar = document.getElementById('shopNavbar');

    // Add event listeners for collapse show/hide
    shopNavbar.addEventListener('show.bs.collapse', function () {
        navbarLabel.innerHTML = '<a href="/shop" class="text-light">Reset</a>';
    });

    shopNavbar.addEventListener('hide.bs.collapse', function () {
        navbarLabel.textContent = 'Shop';
    });
});

// Check if URL has any query parameters
function hasQueryParams() {
    return window.location.search.length > 0;
}

// On page load, expand navbar if query paremeters exist
document.addEventListener("DOMContentLoaded", function () {
    const shopNavbar = document.getElementById('shopNavbar');

    if (hasQueryParams()) {
        const bsCollapse = new bootstrap.Collapse(shopNavbar, {
            toggle: false // Prevent Bootstrap from automatically toggling
        });
        bsCollapse.show(); // Manually show the navbar
    }
});