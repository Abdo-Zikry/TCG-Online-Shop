from cryptography.fernet import Fernet
from flask import flash

import bcrypt, binascii, db, os, re

NAME_REGEX = re.compile(r'^[A-Za-z\s]+$')
EMAIL_REGEX = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
CREDIT_CARD_REGEX = r'^\d{4} \d{4} \d{4} \d{4}$'
PASSWORD_REGEX = re.compile(r'^(?=.*\d)(?=.*[a-z])(?=.*[A-Z]).{8,20}$')

def valid_registration(user):
    if not NAME_REGEX.match(user['first_name']):
        flash('First name can only contain letters and spaces.', 'warning')
        return False
    if len(user['first_name']) > 50:
        flash('First name cannot exceed 50 characters.', 'danger')
        return False
    if not NAME_REGEX.match(user['last_name']):
        flash('Last name can only contain letters and spaces.', 'warning')
        return False
    if len(user['last_name']) > 50:
        flash('Last name cannot exceed 50 characters.', 'danger')
        return False
    if not re.match(EMAIL_REGEX, user['email']):
        flash('Invalid email address format.', 'danger')
        return False
    if db.check_email(user['email']):
        flash('A user with this email already exists.', 'warning')
        return False
    if len(user['email']) > 255:
        flash('Email address is too long (max 255 characters).', 'danger')
        return False
    if not re.match(CREDIT_CARD_REGEX, user['credit_card']):
        flash('Invalid credit card format.', 'danger')
        return False
    if not PASSWORD_REGEX.match(user['password']):
        flash('Password must be 8-20 characters, with at least one uppercase, lowercase, and number.', 'danger')
        return False
    if user['password'] != user['confirm_password']:
        flash('Passwords do not match.', 'danger')
        return False
    return True

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

def valid_changes(new):
    if not NAME_REGEX.match(new['first_name']):
        flash('First name can only contain letters and spaces.', 'warning')
        return False
    if len(str(new['first_name'])) > 50:
        flash('First name cannot exceed 50 characters.', 'warning')
        return False
    if not NAME_REGEX.match(new['last_name']):
        flash('Last name can only contain letters and spaces.', 'warning')
        return False
    if len(str(new['last_name'])) > 50:
        flash('Last name cannot exceed 50 characters.', 'warning')
        return False
    if not re.match(EMAIL_REGEX, new['email']):
        flash("Invalid email format. Please enter a valid email address.", "danger")
        return False
    if len(str(new['email'])) > 255:
        flash('Your email is too long. Please enter a shorter one', 'warning')
        return False
    if not PASSWORD_REGEX.match(new['password']):
        flash('Password must be 8-20 characters long, include at least one uppercase letter, one lowercase letter, and one number.', 'danger')
        return False
    if new['password'] != new['confirm_password']:
        flash('Passwords do not match.', 'danger')
        return False
    return True