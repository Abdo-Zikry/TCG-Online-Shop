from flask import flash, redirect
from cryptography.fernet import Fernet
from datetime import datetime, timedelta
import bcrypt, binascii, db, os, re, sqlite3, security
from werkzeug.utils import escape


NAME_REGEX = re.compile(r'^[A-Za-z\s]+$')
EMAIL_REGEX = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
CREDIT_CARD_REGEX = r'^\d{4} \d{4} \d{4} \d{4}$'
PASSWORD_REGEX = re.compile(r'^(?=.*\d)(?=.*[a-z])(?=.*[A-Z]).{8,20}$')

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
    new['first_name'] = escape(form.get('first_name'))
    new['last_name'] = escape(form.get('last_name'))
    new['email'] = escape(form.get('email'))
    new['address'] = escape(form.get('address'))
    credit_card = escape(form.get('credit_card'))
    if is_credit_card_changed(credit_card):
        new['credit_card'] = credit_card
    else:
        new['credit_card'] = security.decrypt_credit_card(user['credit_card'])
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
    seven_days_ago = datetime.now() - timedelta(days=7)
    seven_days_ago_str = seven_days_ago.strftime('%Y-%m-%d %H:%M:%S')

    connection = sqlite3.connect('database.db')
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()
    query = 'SELECT product_id, amount FROM purchases WHERE time >= ?'
    cursor.execute(query, (seven_days_ago_str,))
    recent_purchases = [dict(row) for row in cursor.fetchall()]
    connection.close()

    recent_purchases_amount = dict()
    for purchase in recent_purchases:
        if purchase['product_id'] in recent_purchases_amount:
            recent_purchases_amount[purchase['product_id']] += purchase['amount']
        else:
            recent_purchases_amount[purchase['product_id']] = purchase['amount']

    sorted_products = sorted(products, key=lambda product: recent_purchases_amount.get(product['id'], 0), reverse=reverse)
    return sorted_products


