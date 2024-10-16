from datetime import datetime
from dotenv import load_dotenv
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_wtf.csrf import CSRFProtect
from flask_session import Session
from werkzeug.utils import escape

import db, os, utilities, security

#setting up the app and security
app = Flask(__name__)

load_dotenv()
app.secret_key = os.getenv('SECRET_KEY')
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)
csrf = CSRFProtect(app)

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
        flash('You are already logged in', 'danger')
        return redirect('/')
    if request.method == 'GET':
        return render_template('register.html')
    if request.method == 'POST':
        user = utilities.create_user(request.form)
        
        if not security.valid_registration(user):
            return redirect('/register')

        encrypted_credit_card = security.encrypt_credit_card(user['credit_card'])
        hashed_password = security.hash_password(user['password'])
        user_id = security.generate_secure_id()

        db.add_user(user_id, user, encrypted_credit_card, hashed_password)
        session['user_id'] = user_id
        
        flash('Registration is successful', 'success')
        return redirect('/')
    
@app.route('/login', methods = ['GET', 'POST'])
def login():
    if 'user_id'in session:
        flash('You are already logged in.', 'danger')
        return redirect('/')
    if request.method == 'GET':
        return render_template('login.html')
    if request.method == 'POST':
        email = escape(request.form.get('email'))
        password = escape(request.form.get('password'))
        user_id = db.authenticate_login(email, password)
        
        if not user_id:
            return redirect('/login')
        session['user_id'] = user_id
        cart = db.retrieve_cart(user_id)
        session['cart'] = cart
        session['cart_count'] = sum(cart.values())
        return redirect('/')
        
@app.route('/logout', methods = ['GET'])
def logout():
    if 'user_id' not in session:
        flash('You have to be logged in to log out.', 'danger')
        return redirect('/login')
    
    db.save_cart(session.get('cart'), session['user_id'])
    session.clear()
    return redirect('/')

@app.route('/settings', methods = ['GET', 'POST'])
def settings():
    if 'user_id' not in session:
            flash('You have to be logged in to access settings', 'danger')
            return redirect('/')

    if request.method == 'GET':
        user = db.get_user(session['user_id'])
        last_four_digits = security.decrypt_credit_card(user['credit_card'])[-4:]
        return render_template('settings.html', user=user, last_four_digits=last_four_digits)
    
    if request.method == 'POST':
        user = db.get_user(session['user_id'])
        password = escape(request.form.get('password'))
        if not db.check_password(user['id'], password):
            flash('You entered wrong password. All changes are discarded.', 'warning')
            return redirect('/settings')
        
        new = utilities.record_changes(request.form, user['id'], password)
        if new['email'] != user['email']:
            if db.check_email(new['email']):
                flash('That email is already used', 'warning')
                return redirect('/settings')

        if not security.valid_changes(new):
            return redirect('/settings')
        
        db.update_user(new, session['user_id'])
        flash('Changes were updated successfully', 'success')
        return redirect('/')

@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'GET':
        return render_template('search.html')
    if request.method == 'POST':
        text = escape(request.form.get('search'))
        products = db.search_products(text)

        today = datetime.now().date()
        for product in products:
            product['release_date'] = datetime.strptime(product['release_date'], '%Y-%m-%d')
        
        return render_template('search.html', products=products, today=today)
    
@app.route('/shop', methods = ['GET'])
def shop():
    #retrieve filtering and sorting parameters
    selected_games = request.args.getlist('game')
    selected_type = request.args.get('type')
    sort = request.args.get('sort', 'popularity')
    order = request.args.get('order', 'desc')

    #filtering prooducts
    if selected_games:
        products = db.select_products_by_games(selected_games)
    else:
        products = db.get_all_products()
    if selected_type:
        products = [product for product in products if product['type'] in selected_type]

    #sorting products
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
    name = escape(request.args.get('product'))
    product = db.get_product(name)

    return render_template('product_details.html', product=product)

@app.route('/purchase', methods=['GET', 'POST'])
def purchase():
    if 'user_id' not in session:
        flash('You have to be logged in to purchase products', 'warning')
        return redirect('/login')
    
    if request.method == 'POST':
        product_name = escape(request.form.get('product_name'))
        product = db.get_product(product_name)
        saved_url = request.form.get('current_url')
        
        if not product:
            flash('This product does not exist', 'danger')
            return redirect(saved_url)
        if product['amount'] == 0:
            flash('Cannot purchase, product is sold out', 'danger')
            return redirect(saved_url)
        
        user = db.get_user(session['user_id'])
        last_four_digits = security.decrypt_credit_card(user['credit_card'])[-4:]

        session['product_data'] = product
        session['saved_url'] = saved_url

        return render_template('purchase.html', user=user, product=product, saved_url=saved_url, last_four_digits=last_four_digits)
                
    if request.method == 'GET':
        product = session.get('product_data')
        saved_url = session.get('saved_url')

        if product['amount'] == 0:
            flash('Cannot purchase, product is sold out', 'danger')
            return redirect(saved_url)
        
        db.add_purchase(session['user_id'], product['id'], 1)
        flash('Purchase was successful.', 'success')
        return redirect(saved_url)    

@app.route('/cart', methods=['GET'])
def cart():
    if 'user_id' not in session:
        flash('You have to be logged in to access cart.', 'warning')
        return redirect('/login')
    
    if 'cart' not in session:
        flash('Cart is empty. Add products to cart to access it.', 'warning')
        return redirect('/')
    
    cart = session.get('cart')
    if sum(cart.values()) == 0:
        flash('Cart is empty. Add products to cart to access it.', 'warning')
        return redirect('/')
    
    products = list()
    for product_id in cart.keys():
        product = db.get_product(product_id)
        product['cart_count'] = cart[product_id]
        products.append(product)
    
    return render_template('cart.html', products=products)
    
@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    if 'user_id' not in session:
        flash('You have to be logged in to proceed to checkout.', 'danger')
        return redirect('/login')
    if 'cart' not in session:
        flash('Cart is empty. Nothing to checkout.', 'danger')
        return redirect('/')
    cart = session.get('cart')
    if sum(cart.values()) == 0:
        flash('Cart is empty. Nothing to checkout.', 'danger')
        return redirect('/')
    
    products = []
    for product_id in cart.keys():
        product = db.get_product(product_id)
        product['cart_count'] = cart[product_id]
        products.append(product)

    user = db.get_user(session['user_id'])

    if request.method == 'GET':
        total_price = 0
        for product in products:
            total_price += product['cart_count'] * product['price']

        last_four_digits = security.decrypt_credit_card(user['credit_card'])[-4:]

        return render_template('checkout.html', products=products, user=user, total_price=total_price, last_four_digits=last_four_digits)
    
    if request.method == 'POST':
        for product in products:
            if product['cart_count'] < 0:
                flash(f'You cannot request negative amount of {product['name']}.', 'danger')
                return redirect('/cart')
            if product['cart_count'] > product['amount']:
                flash(f'Requested amount of {product['name']} is larger than what is in stock. There is only {product['amount']} left.', 'danger')
                return redirect('/cart')
            
        for product in products:
            db.add_purchase(session['user_id'], product['id'], product['cart_count'])

        session.pop('cart', None)
        session.pop('cart_count', None)

        flash('Your purchases were successful. You can check them in your orders page.', 'success')
        return redirect('/')

@app.route('/orders', methods=['GET'])
def orders():
    if 'user_id' not in session:
        flash('You have to be logged in to view orders', 'danger')
        return redirect('/login')
    
    orders = db.get_orders(session['user_id'])
    return render_template('orders.html', orders=orders)


#Javascript target routes
@app.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    if 'user_id' not in session:
        return jsonify(success=False, message="You have to be logged in to add to cart.")

    data = request.get_json()
    product_id = data['product_id']
    max_stock = int(data['max_stock'])

    cart = session.get('cart', {})
    # Check if cart amount is less than or equal to max stock and handle it
    if product_id in cart:
        if cart[product_id] < max_stock:
            cart[product_id] += 1
        elif cart[product_id] == max_stock:
            cart[product_id] = max_stock
            session['cart'] = cart
            session['cart_count'] = sum(cart.values())
            return jsonify(success=False, message="Sorry, you already have the maximum available stock of this product in your cart.")
        else:
            # If cart amount is larger than what's in stock update it to match max stock
            cart[product_id] = max_stock
            session['cart'] = cart
            session['cart_count'] = sum(cart.values())
            return jsonify(success=True, cart_count=session['cart_count'])
    else:
        cart[product_id] = 1

    session['cart'] = cart

    if 'cart_count' in session:
        session['cart_count'] += 1
    else:
        session['cart_count'] = 1

    return jsonify(success=True, cart_count=session['cart_count'])

@app.route('/update_cart', methods=['POST'])
def update_cart():
    data = request.get_json()
    product_id = data['product_id']
    new_quantity = data['new_quantity']

    cart = session.get('cart', {})

    if new_quantity == 0:
        cart.pop(str(product_id), None)
    else:
        cart[str(product_id)] = new_quantity

    session['cart'] = cart
    session['cart_count'] = sum(cart.values())

    return jsonify(success=True, cart_count=session['cart_count'])
    
@app.route('/save_cart', methods=['POST'])
def save_cart():
    if 'user_id' not in session:
        return jsonify({'status': 'User not logged in!'}), 403

    cart_data = session.get('cart')
    user_id = session.get('user_id')
    db.save_cart(cart_data, user_id)

    return jsonify({'status': 'Cart saved successfully!'}), 200
        

if __name__ == '__main__':
    app.run(debug=True)