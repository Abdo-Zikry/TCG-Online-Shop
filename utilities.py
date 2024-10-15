from datetime import datetime, timedelta
from werkzeug.utils import escape

import db, re, security, sqlite3

def create_user(form):
    user = dict()
    user['first_name'] = escape(form.get('first_name'))
    user['last_name'] = escape(form.get('last_name'))
    user['email'] = escape(form.get('email'))
    user['address'] = escape(form.get('address'))
    user['credit_card'] = escape(form.get('credit_card'))
    user['password'] = escape(form.get('password'))
    user['confirm_password'] = escape(form.get('confirm_password'))
    return user

def record_changes(form, user_id, password):
    user = db.get_user_by_id(user_id)
    new = dict()
    # Retrieve each input
    new['first_name'] = escape(form.get('first_name'))
    new['last_name'] = escape(form.get('last_name'))
    new['email'] = escape(form.get('email'))
    new['address'] = escape(form.get('address'))
    credit_card = escape(form.get('credit_card'))

    # Get new credit card if changed
    if is_credit_card_changed(credit_card):
        new['credit_card'] = credit_card
    else:
        new['credit_card'] = security.decrypt_credit_card(user['credit_card'])

    # Get new password if changed
    new_password = escape(form.get('new_password'))
    if new_password:
        new['password'] = new_password
        new['confirm_password'] = escape(form.get('confirm_new_password'))
    else:
        new['password'] = password
        new['confirm_password'] = password

    return new

def is_credit_card_changed(credit_card):
    # Regular expression to match **** **** **** 5672 pattern
    pattern = r"^\*\*\*\* \*\*\*\* \*\*\*\* \d{4}$"
    return not bool(re.match(pattern, credit_card))
    
def sort_by_popularity(products, reverse):
    seven_days_ago = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d %H:%M:%S')

    connection = sqlite3.connect('database.db')
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()

    # Retrieve purchases made in the past week
    query = 'SELECT product_id, amount FROM purchases WHERE time >= ?'
    cursor.execute(query, (seven_days_ago,))
    recent_purchases = [dict(row) for row in cursor.fetchall()]
    connection.close()

    # Calculate the total amount purchased for each product
    recent_purchases_amount = dict()
    for purchase in recent_purchases:
        if purchase['product_id'] in recent_purchases_amount:
            recent_purchases_amount[purchase['product_id']] += purchase['amount']
        else:
            recent_purchases_amount[purchase['product_id']] = purchase['amount']

    sorted_products = sorted(products, key=lambda p: recent_purchases_amount.get(p['id'], 0), reverse=reverse)
    return sorted_products