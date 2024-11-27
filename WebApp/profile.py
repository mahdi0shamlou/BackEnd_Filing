from flask import Blueprint, jsonify, request
import re
# -------------jwt tokens
from flask_jwt_extended import jwt_required, get_jwt_identity
# -------------
# ------------- models
from models import users as Users
from models import db
# ---------------

profile_bp = Blueprint('profile', __name__)

# Regular expression for validating email format
def validate_email(email):
    email_regex = r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"
    return re.match(email_regex, email) is not None

@profile_bp.route('/Profile', methods=['GET'])
@jwt_required()
def profile_user():
    # Get the current logged-in user's phone number from the JWT token
    current_user = get_jwt_identity()
    user_phone = current_user['phone']

    # Query the 'users' table for a user with the matching phone number
    user = Users.query.filter_by(phone=user_phone).first()

    # Check if the user exists
    if user:
        # Return the user data as JSON
        user_data = {
            'id': user.id,
            'username': user.username,
            'name': user.name,
            'phone': user.phone,
            'address': user.address,
            'email': user.email,
            'created_at': user.created_at.isoformat(),
            'updated_at': user.updated_at.isoformat() if user.updated_at else None
        }
        return jsonify(user_data), 200

    # If the user is not found, return an error response
    return jsonify({"message": "خطا کاربر مورد نظر یافت نشد !"}), 404


@profile_bp.route('/Profile/edit', methods=['PATCH'])
@jwt_required()
def edit_user_profile():
    current_user = get_jwt_identity()
    user_phone = current_user['phone']

    # Fetch the user from the database using the phone number (assumed to be unique)
    user = Users.query.filter_by(phone=user_phone).first()

    if not user:
        return jsonify({"message": "خطا کاربر مورد نظر یافت نشد !"}), 404

    # Get the data from the request body
    data = request.get_json()

    # Update only the fields that are provided in the request
    if 'name' in data:
        new_name = data['name']
        if not new_name.strip():
            return jsonify({"message": "نام را خالی نزارید ."}), 400
        if len(new_name) > 50:
            return jsonify({"message": "تعداد کارکتر های شما برای نام خیلی زیاد است . حداکثر ۵۰"}), 400
        user.name = new_name

    if 'address' in data:
        new_address = data['address']
        if len(new_address) > 100:
            return jsonify({"message": "حداکثر کاراکتر برای آدرس ۱۰۰ عدد است ."}), 400
        user.address = new_address  # Address can be updated freely, no special validation

    if 'email' in data:
        new_email = data['email']
        if len(new_email) > 100:
            return jsonify({"message": "حداکثر تعداد کارکتر برای ایمیل ۱۰۰ عدد است ."}), 400
        if not validate_email(new_email):
            return jsonify({"message": "ایمیل وارد شده صحیح نیست ."}), 400
        # Check if the email already exists in the database
        existing_email = Users.query.filter_by(email=new_email).first()
        if existing_email and existing_email.id != user.id:
            return jsonify({"message": "این ایمیل قبلا ثبت شده است !"}), 400
        user.email = new_email

    # Commit changes to the database
    db.session.commit()

    # Return the updated user data
    user_data = {
        'id': user.id,
        'username': user.username,
        'name': user.name,
        'phone': user.phone,
        'address': user.address,
        'email': user.email,
        'created_at': user.created_at.isoformat(),
        'updated_at': user.updated_at.isoformat() if user.updated_at else None
    }

    return jsonify(user_data), 200