from flask import flash, redirect
from cryptography.fernet import Fernet
from datetime import datetime, timedelta
import bcrypt, binascii, db, os, re, sqlite3

NAME_REGEX = re.compile(r'^[A-Za-z\s]+$')
EMAIL_REGEX = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
CREDIT_CARD_REGEX = r'^\d{4} \d{4} \d{4} \d{4}$'
PASSWORD_REGEX = re.compile(r'^(?=.*\d)(?=.*[a-z])(?=.*[A-Z]).{8,20}$')

def validate_registration(user):
    if not NAME_REGEX.match(user['first_name']):
        flash('First name can only contain letters and spaces.', 'warning')
        return True
    if len(str(user['first_name'])) > 50:
        flash('First name cannot exceed 50 characters.', 'warning')
        return True
    if not NAME_REGEX.match(user['last_name']):
        flash('Last name can only contain letters and spaces.', 'warning')
        return True
    if len(str(user['last_name'])) > 50:
        flash('Last name cannot exceed 50 characters.', 'warning')
        return True
    if not re.match(EMAIL_REGEX, user['email']):
        flash("Invalid email format. Please enter a valid email address.", "danger")
        return True
    if db.check_email(str(user['email'])):
        flash('A user with this email already exists', 'warning')
        return True
    if len(str(user['email'])) > 255:
        flash('Your email is too long. Please enter a shorter one', 'warning')
        return True
    if not re.match(CREDIT_CARD_REGEX, user['credit_card']):
        flash("Invalid credit card format. Use a valid credit card", "danger")
        return True
    if not PASSWORD_REGEX.match(user['password']):
        flash('Password must be 8-20 characters long, include at least one uppercase letter, one lowercase letter, and one number.', 'danger')
        return True
    if user['password'] != user['confirm_password']:
        flash('Passwords do not match.', 'danger')
        return True
    return False

def validate_new(user):
    if not NAME_REGEX.match(user['first_name']):
        flash('First name can only contain letters and spaces.', 'warning')
        return True
    if len(str(user['first_name'])) > 50:
        flash('First name cannot exceed 50 characters.', 'warning')
        return True
    if not NAME_REGEX.match(user['last_name']):
        flash('Last name can only contain letters and spaces.', 'warning')
        return True
    if len(str(user['last_name'])) > 50:
        flash('Last name cannot exceed 50 characters.', 'warning')
        return True
    if not re.match(EMAIL_REGEX, user['email']):
        flash("Invalid email format. Please enter a valid email address.", "danger")
        return True
    if len(str(user['email'])) > 255:
        flash('Your email is too long. Please enter a shorter one', 'warning')
        return True
    if not PASSWORD_REGEX.match(user['password']):
        flash('Password must be 8-20 characters long, include at least one uppercase letter, one lowercase letter, and one number.', 'danger')
        return True
    if user['password'] != user['confirm_password']:
        flash('Passwords do not match.', 'danger')
        return True


def is_credit_card_changed(credit_card):
    # Regular expression to match **** **** **** 5672 pattern
    pattern = r"^\*\*\*\* \*\*\*\* \*\*\*\* \d{4}$"
    return not bool(re.match(pattern, credit_card))
    
def generate_secure_id(length=16):
    return binascii.hexlify(os.urandom(length)).decode('utf-8')


def hash_password(password):
    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    return hashed.decode('utf-8')

def encrypt_credit_card(credit_card):
    CREDIT_CARD_KEY = os.getenv('CREDIT_CARD_KEY')
    cipher_suite = Fernet(CREDIT_CARD_KEY)
    encrypted_credit_card = cipher_suite.encrypt(credit_card.encode('utf-8'))
    return encrypted_credit_card.decode('utf-8')

def decrypt_credit_card(encrypted_credit_card):
    CREDIT_CARD_KEY = os.getenv('CREDIT_CARD_KEY')
    cipher_suite = Fernet(CREDIT_CARD_KEY)
    decrypted_credit_card = cipher_suite.decrypt(encrypted_credit_card.encode('utf-8'))
    return decrypted_credit_card.decode('utf-8')

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


