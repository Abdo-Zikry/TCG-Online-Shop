import db, os, utilities

from flask import Flask, flash, jsonify, redirect, render_template, request, session
from datetime import datetime
from dotenv import load_dotenv
from flask_session import Session
from werkzeug.utils import escape

app = Flask(__name__)

load_dotenv()
app.secret_key = os.getenv('SECRET_KEY')
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

@app.route('/')
def index():
    products = db.get_all_products()
    products = utilities.sort_by_popularity(products, reverse=True)
    products = products[:8]

    today = datetime.now().date()
    for product in products:
        product['release_date'] = datetime.strptime(product['release_date'], '%Y-%m-%d')

    return render_template('index.html', display_products=products, today=today)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if 'user_id' in session:
        return redirect('/')
    if request.method == 'GET':
        return render_template('register.html')
    if request.method == 'POST':
        user = dict()
        user['first_name'] = escape(request.form.get('first_name'))
        user['last_name'] = escape(request.form.get('last_name'))
        user['email'] = escape(request.form.get('email'))
        user['address'] = escape(request.form.get('address'))
        user['credit_card'] = escape(request.form.get('credit_card'))
        user['password'] = escape(request.form.get('password'))
        user['confirm_password'] = escape(request.form.get('confirm_password'))
        
        if utilities.validate_registration(user):
            return redirect('/register')

        encrypted_credit_card = utilities.encrypt_credit_card(user['credit_card'])
        hashed_password = utilities.hash_password(user['password'])
        
        user_id = utilities.generate_secure_id()
        session['user_id'] = user_id
        db.add_user(user_id, user['first_name'], user['last_name'], user['email'], user['address'], encrypted_credit_card, hashed_password)
        flash("Registration is successful", "success")
        return redirect('/')
    
@app.route('/login', methods = ['GET', 'POST'])
def login():
    if 'user_id'in session:
        return redirect('/')
    if request.method == 'GET':
        return render_template('login.html')
    if request.method == 'POST':
        email = escape(request.form.get('email'))
        password = escape(request.form.get('password'))
        user = db.get_user_by_email(email)
        if not user:
            flash('There is no user with such email', 'warning')
            return redirect('/login')
        if not db.check_password(email, password):
            flash('Password is not correct', 'warning')
            return redirect('/login')
        
        session['user_id'] = user['id']
        flash('Log in is successful', 'success')
        return redirect('/')
        
    
@app.route('/logout', methods = ['GET'])
def logout():
    session.pop('user_id', None)
    session.pop('user_data', None)
    session.pop('product_data', None)
    session.pop('saved_url', None)
    session.pop('cart', None)
    session.pop('products_in_cart', None)

    return redirect('/')

@app.route('/settings', methods = ['GET', 'POST'])
def settings():
    if request.method == 'GET':
        if 'user_id' not in session:
            flash('You have to be logged in to access settings', 'danger')
            return redirect('/')
        
        user = db.get_user_by_id(session['user_id'])
        last_four_digits = utilities.decrypt_credit_card(user['credit_card'])[-4:]
        return render_template('settings.html', user=user, last_four_digits=last_four_digits)
    
    if request.method == 'POST':
        if 'user_id' not in session:
            flash('You have to be logged in to access settings', 'danger')
            return redirect('/')
        
        user = db.get_user_by_id(session['user_id'])
        password = escape(request.form.get('password'))
        if not db.check_password(user['email'], password):
            flash('You entered wrong password. All changes are discarded.', 'warning')
            return redirect('/settings')
        
        new = dict()
        new['first_name'] = escape(request.form.get('first_name'))
        new['last_name'] = escape(request.form.get('last_name'))
        new['email'] = escape(request.form.get('email'))
        if new['email'] != user['email']:
            if db.get_user_by_email(new['email']):
                flash('That email is already used', 'warning')
                return redirect('/settings')
        new['address'] = escape(request.form.get('address'))

        credit_card = escape(request.form.get('credit_card'))
        if utilities.is_credit_card_changed(credit_card):
            new['credit_card'] = credit_card
        else:
            new['credit_card'] = utilities.decrypt_credit_card(user['credit_card'])

        new_password = escape(request.form.get('new_password'))
        if new_password:
            new['password'] = new_password
            new['confirm_password'] = escape(request.form.get('confirm_new_password'))
        else:
            new['password'] = password
            new['confirm_password'] = password

        if utilities.validate_new(new):
            return redirect('/settings')
        
        db.update_user(new, session['user_id'])
        flash('Changes were updated successfully', 'success')
        return redirect('/')

@app.route('/shop', methods = ['GET', 'POST'])
def shop():
    selected_games = request.args.getlist('game')
    selected_type = request.args.get('type')
    sort = request.args.get('sort', 'popularity')
    order = request.args.get('order', 'desc')
    if selected_games:
        products = db.select_products_by_games(selected_games)
    else:
        products = db.get_all_products()
    if selected_type:
        products = [product for product in products if product['type'] in selected_type]

    reverse_order = (order == 'desc')
    if sort == 'popularity':
        products = utilities.sort_by_popularity(products, reverse=reverse_order)
    elif sort == 'release_date':
        products = sorted(products, key=lambda p: p['release_date'], reverse=reverse_order)
    elif sort == 'alphabetical':
        products = sorted(products, key=lambda p: p['name'], reverse=reverse_order)

    today = datetime.now().date()
    for product in products:
        product['release_date'] = datetime.strptime(product['release_date'], '%Y-%m-%d')


    return render_template('shop.html', products=products, today=today, selected_games=selected_games, selected_type=selected_type, sort=sort, order=order)

@app.route('/product_details', methods=['GET'])
def product_details():
    name = request.args.get('product')
    product = db.get_product(name)

    return render_template('product_details.html', product=product)


@app.route('/confirm_payment', methods=['POST'])
def confirm_payment():
    if 'user_id' not in session:
        flash('You have to be logged in to purchase products', 'warning')
        return redirect('/login')
    
    product_name = escape(request.form.get('product_name'))
    product = db.get_product(product_name)
    saved_url = request.form.get('current_url')

    if product['amount'] == 0:
        flash('Cannot purchase, product is sold out', 'danger')
        return redirect(saved_url)
    
    user = db.get_user_by_id(session['user_id'])
    last_four_digits = utilities.decrypt_credit_card(user['credit_card'])[-4:]

    session['user_data'] = user
    session['product_data'] = product
    session['saved_url'] = saved_url

    return render_template('confirm_payment.html', user=user, product=product, saved_url=saved_url, last_four_digits=last_four_digits)
    

@app.route('/purchase', methods=['GET'])
def purchase():
    if 'user_id' not in session:
        flash('You have to be logged in to purchase products', 'danger')
        return redirect('/login')

    product = session.get('product_data')
    saved_url = session.get('saved_url')

    if product['amount'] == 0:
        flash('Cannot purchase, product is sold out', 'danger')
        return redirect(saved_url)
    
    db.add_purchase(session['user_id'], product['id'], 1)

    return redirect('/successful_purchase')
    

@app.route('/successful_purchase', methods=['GET'])
def successful_purchase():
    if any(key not in session for key in ('user_data', 'product_data', 'saved_url')):
        flash('You can only access this page after completing a purchase.', 'danger')
        return redirect('/')

    user = session.get('user_data')
    product = session.get('product_data')
    saved_url = session.get('saved_url')

    last_four_digits = utilities.decrypt_credit_card(user['credit_card'])[-4:]
    
    return render_template('purchased.html', product=product, user=user, saved_url=saved_url, last_four_digits=last_four_digits)


@app.route('/add_to_cart_ajax', methods=['POST'])
def add_to_cart_ajax():
    if 'user_id' not in session:
        # User is not logged in, return an error message
        return jsonify(success=False, message="You have to be logged in first.")

    data = request.get_json()
    product_id = data['product_id']

    # Get cart from session or initialize it if it doesn't exist
    cart = session.get('cart', {})
    if product_id in cart:
        cart[product_id] += 1
    else:
        cart[product_id] = 1

    session['cart'] = cart

    # Update the products in cart count
    session['products_in_cart'] = sum(cart.values())

    return jsonify(success=True, products_in_cart=session['products_in_cart'])



@app.route('/cart', methods=['GET', 'POST'])
def card():
    if 'user_id' not in session:
        flash('You have to log in first.', 'warning')
        return redirect('/')
    
    if 'cart' not in session:
        flash('Nothing in cart yet.', 'warning')
        return redirect('/')
    
    cart = session.get('cart')
    if sum(cart.values()) == 0:
        flash('Cart is now empty.', 'warning')
        return redirect('/')
    
    if request.method == 'GET':
        products = []
        if cart:
            for product_id in cart.keys():
                product = db.get_product_by_id(product_id)
                product['amount_in_cart'] = cart[product_id]
                products.append(product)
        

        return render_template('cart.html', cart=cart, cart_products=products)
    
@app.route('/update_cart', methods=['POST'])
def update_cart():
    data = request.get_json()
    product_id = data['product_id']
    new_quantity = data['new_quantity']

    # Get cart from session or initialize if not available
    cart = session.get('cart', {})

    if new_quantity == 0:
        # If quantity is 0, remove the item from the cart
        cart.pop(str(product_id), None)
    else:
        # Update the quantity for the specified product
        cart[str(product_id)] = new_quantity

    # Save the updated cart in session
    session['cart'] = cart

    # Update total number of products in cart
    session['products_in_cart'] = sum(cart.values())

    return jsonify(success=True, products_in_cart=session['products_in_cart'])

@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    if 'user_id' not in session:
        flash('You have to be logged in to proceed to checkout.', 'danger')
        return redirect('/login')
    if 'cart' not in session:
        flash('Nothing is in cart to checkout.', 'danger')
        return redirect('/')
    cart = session.get('cart')
    if sum(cart.values()) == 0:
        flash('Cart is empty. Nothing to checkout.', 'danger')
        return redirect('/')
    
    products = []
    for product_id in cart.keys():
        product = db.get_product_by_id(product_id)
        product['amount_in_cart'] = cart[product_id]
        products.append(product)

    user = db.get_user_by_id(session['user_id'])

    if request.method == 'GET':
        total_price = 0
        for product in products:
            total_price += product['amount_in_cart'] * product['price']

        last_four_digits = utilities.decrypt_credit_card(user['credit_card'])[-4:]

        return render_template('checkout.html', products=products, user=user, total_price=total_price, last_four_digits=last_four_digits)
    
    if request.method == 'POST':
        for product in products:
            if product['amount_in_cart'] < 0:
                flash(f'You cannot request negative amount of {product['name']}.', 'danger')
                return redirect('/cart')
            if product['amount_in_cart'] > product['amount']:
                flash(f'Requested amount of {product['name']} is larger than what is in stock.', 'danger')
                return redirect('/cart')
            
        for product in products:
            db.add_purchase(session['user_id'], product['id'], product['amount_in_cart'])

        session.pop('cart', None)
        session.pop('products_in_cart', None)

        flash('Your purchases were successful. You can check them in orders.', 'success')
        return redirect('/')



@app.route('/orders', methods=['GET'])
def orders():
    if 'user_id' not in session:
        flash('You have to be logged in to view orders', 'danger')
        return redirect('/login')
    
    orders = db.get_all_orders(session['user_id'])
    return render_template('orders.html', orders=orders)

@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'GET':
        return render_template('search.html')
    if request.method == 'POST':
        
        text = escape(request.form.get('search'))
        products = db.get_products_by_search(text)
        today = datetime.now().date()
        for product in products:
            product['release_date'] = datetime.strptime(product['release_date'], '%Y-%m-%d')
        
        return render_template('search.html', products=products, today=today)


if __name__ == '__main__':
    app.run(debug=True)