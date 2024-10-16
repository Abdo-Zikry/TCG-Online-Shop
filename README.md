
# Card Haven - TCG Online Shop

**Where Card Masters Shop**

Welcome to **Card Haven**, an online shop for TCG (Trading Card Games). This project is a web application built using Python and Flask, offering a streamlined e-commerce experience with features like browsing products, filtering items, adding items to the cart, and purchasing products.

## Table of Contents
1. [Project Overview](#project-overview)
2. [Features](#features)
3. [Installation](#installation)
4. [Usage](#usage)
5. [Project Structure](#project-structure)
6. [Technologies Used](#technologies-used)
7. [Screenshots](#screenshots)
8. [Future Enhancements](#future-enhancements)
9. [License](#license)

## Project Overview

Card Haven is a mock online shop where users can:
- Use filters for card games like **Yu-Gi-Oh!**, **Digimon**, **Chaotic**, and **Cardfight: Vanguard**.
- Purchase products securely by providing shipping information and payment details.
- Add items to their cart and update quantities.
- View past orders and update account settings.

This project was created for practice in web development, focusing on backend logic with Flask and frontend user experience with Bootstrap.

## Features

- **Product Browsing**: View products with images, descriptions, and prices.
- **Filtering & Sorting**: Filter products by card game and product type, and sort them by popularity, release date, or alphabetically.
- **Cart Management**: Add products to the cart, update product quantities, and remove products from the cart.
- **User Authentication**: Register, login, and access personalized user settings.
- **Purchase Flow**: Complete purchases and view an order summary with the last four digits of your credit card for confirmation.
- **User Settings**: Update user profile, shipping address, and payment details.

## Installation

### Prerequisites

- Python 3.x
- Flask
- SQLite (or any preferred database)

### Steps

1. Clone this repository:
   ```bash
   git clone https://github.com/Abdo-Zikry/TCG-Online-Shop.git
   ```
2. Navigate to the project directory:
   ```bash
   cd TCG-Online-Shop
   ```
3. Install required Python packages

4. Set up environment variables in a `.env` file:
   ```env
   SECRET_KEY=<your_secret_key>
   CREDIT_CARD_KEY=<your_credit_card_key>
   ```
5. Run the Flask development server:
   ```bash
   flask run
   ```

## Usage

Once the server is running, you can access the application by opening your web browser and navigating to:
```
http://127.0.0.1:5000/
```

### Key Pages:
- **Homepage**: Lists top 8 popular products.
- **Shop**: Views all products and allows filtering and sorting.
- **Product Details**: Provides more details about each product, including the ability to purchase or add to the cart.
- **Cart**: Displays products added to the cart and allows users to proceed to checkout.
- **Orders**: Users can view their previous purchases.
- **Settings**: Users can update their profile information.

## Project Structure

```
C:/Users/USER/TCG-Online-Shop/
│
├── static/
│   ├── assets/
│   ├── css/
│   │   └── styles.css
│   ├── js/
│   │   └── scripts.js
│   └── products/
│
├── templates/
│   ├── index.html
│   ├── shop.html
│   ├── search.html
│   ├── cart.html
│   └── ...
│
├── app.py
├── database.py
├── db.py
├── security.py
└── utilities.py
```

- **static/**: Contains static assets like CSS, JS, and images.
- **templates/**: Contains all the HTML templates for the app.
- **app.py**: The main application file.
- **db.py**: Contains the database functions.
- **securiy.py**: Contains security functions.
- **utilities.py**: Contains some utility functions.

## Technologies Used

- **Backend**: Python, Flask, SQLite
- **Frontend**: HTML, CSS (Bootstrap), JavaScript
- **Session Management**: Flask-Session
- **CSRF Protection**: Flask-WTF
- **Database**: SQLite
- **Static Assets Optimization**: PurgeCSS

## Screenshots

## Screenshots

1. Homepage
![Homepage](static/assets/README%20Images/Home.png)
2. Shop Page
![Shop Page](static/assets/README%20Images/Shop.png)
3. Product Page
![Product Page](static/assets/README%20Images/Product.png) 
4. Cart Page
![Cart Page](static/assets/README%20Images/Cart.png) 
5. Orders Page
![Orders Page](static/assets/README%20Images/Orders.png)  


## Future Enhancements

- **Payment Gateway**: Integrate a real payment processor (e.g., Stripe, PayPal).
- **Product Reviews**: Allow users to leave reviews for products.
- **Inventory Management**: Add admin features for managing products.

## License

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.