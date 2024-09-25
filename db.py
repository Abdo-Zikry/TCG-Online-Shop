from flask import flash, redirect
import bcrypt, sqlite3, utilities

def add_user(id, first_name, last_name, email, address, credit_card, password):
    connection = sqlite3.connect('database.db')
    cursor = connection.cursor()
    query = 'INSERT INTO users (id, first_name, last_name, email, address, credit_card, password) VALUES (?, ?, ?, ?, ?, ?, ?)'
    cursor.execute(query, (id, first_name, last_name, email, address, credit_card, password))
    connection.commit()
    connection.close()

def get_user_by_email(email):
    connection = sqlite3.connect('database.db')
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()
    query = 'SELECT * FROM users WHERE email = ?'
    cursor.execute(query, (email,))
    user = cursor.fetchone()
    if not user:
        return None
    connection.close()
    return dict(user)

def get_user_by_id(id):
    connection = sqlite3.connect('database.db')
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()
    query = 'SELECT * FROM users WHERE id = ?'
    cursor.execute(query, (id,))
    user = cursor.fetchone()
    connection.close()
    return dict(user)

def update_user(user, user_id):
    user['password'] = utilities.hash_password(user['password'])
    user['credit_card'] = utilities.encrypt_credit_card(user['credit_card'])
    connection = sqlite3.connect('database.db')
    cursor = connection.cursor()
    query = 'UPDATE users SET first_name = ?, last_name = ?, email = ?, address= ?, credit_card = ?, password = ? WHERE id = ?'
    cursor.execute(query, (user['first_name'], user['last_name'], user['email'], user['address'], user['credit_card'], user['password'], user_id))
    connection.commit()
    connection.close()

def check_email(email):
    connection = sqlite3.connect('database.db')
    cursor = connection.cursor()
    query = 'SELECT * FROM users WHERE email = ?'
    cursor.execute(query, (email,))
    user = cursor.fetchone()
    connection.close()
    return user
    
def check_password(email, password):
    connection = sqlite3.connect('database.db')
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()
    query = 'SELECT * FROM users WHERE email = ?'
    cursor.execute(query, (email,))
    user = dict(cursor.fetchone())
    connection.close()
    return bcrypt.checkpw(password.encode('utf-8'), user['password'].encode('utf-8'))

def get_product(product_name):
    connection = sqlite3.connect('database.db')
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()
    query = 'SELECT * FROM products WHERE name = ?'
    cursor.execute(query, (product_name,))
    product = dict(cursor.fetchone())
    connection.close()
    return product

def get_product_by_id(product_id):
    connection = sqlite3.connect('database.db')
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()
    query = 'SELECT * FROM products WHERE id = ?'
    cursor.execute(query, (product_id,))
    product = dict(cursor.fetchone())
    connection.close()
    return product

def get_all_products():
    connection = sqlite3.connect('database.db')
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()
    query = 'SELECT * FROM products'
    cursor.execute(query)
    products = [dict(row) for row in cursor.fetchall()]
    connection.close()
    return products

def select_products_by_games(games):
    connection = sqlite3.connect('database.db')
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()
    products = list()
    query = 'SELECT * FROM products WHERE game = ?'
    for game in games:
        cursor.execute(query, (game,))
        for row in cursor.fetchall():
            products.append(dict(row))
    connection.close()
    return products
            
def add_purchase(user_id, product_id, amount):
    connection = sqlite3.connect('database.db')
    cursor = connection.cursor()
    query = 'SELECT amount FROM products WHERE id = ?'
    cursor.execute(query, (product_id,))
    new_amount = cursor.fetchone()[0] - amount
    query = 'UPDATE products SET amount = ? WHERE id = ?'
    cursor.execute(query, (new_amount, product_id))
    user = get_user_by_id(user_id)
    last_four_digits = utilities.decrypt_credit_card(user['credit_card'])[-4:]
    product = get_product_by_id(product_id)
    query = 'INSERT INTO purchases (user_id, product_id, price, amount, shipping_address, credit_last_four) VALUES (?, ?, ?, ?, ?, ?)'
    cursor.execute(query, (user_id, product_id, product['price'], amount, user['address'], last_four_digits))
    connection.commit()
    connection.close()




def get_all_orders(user_id):
    connection = sqlite3.connect('database.db')
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()
    query = '''SELECT pr.name as product_name, pr.image_file_name as product_image, pu.price, pu.shipping_address, pu.credit_last_four, pu.amount, pu.time
        FROM purchases pu JOIN products pr ON pu.product_id = pr.id
        WHERE pu.user_id = ? ORDER BY pu.time DESC'''
    cursor.execute(query, (user_id,))
    orders = [dict(row) for row in cursor.fetchall()]
    connection.close()
    return orders

def get_products_by_search(input):
    connection = sqlite3.connect('database.db')
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()

    # Corrected query with % signs outside of the parameter substitution
    query = 'SELECT * FROM products WHERE name LIKE ?'
    
    # Add the % wildcards around the input
    cursor.execute(query, ('%' + input + '%',))  # Wrap input with wildcards for partial match
    
    products = [dict(row) for row in cursor.fetchall()]
    connection.close()
    return products
