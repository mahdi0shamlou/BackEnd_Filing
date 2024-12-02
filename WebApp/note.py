from flask import Blueprint, jsonify, request
import re
# -------------jwt tokens
from flask_jwt_extended import jwt_required, get_jwt_identity
# -------------
# ------------- models
from models import users as Users
from models import Notes
from models import db
from sqlalchemy import and_
# ---------------

notes_bp = Blueprint('notes', __name__)

# Regular expression for validating email format
def validate_note(note):
    email_regex = r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"
    return re.match(email_regex, note) is not None

@notes_bp.route('/Notes/Get', methods=['GET'])
@jwt_required()
def profile_user():
    # Get the current logged-in user's phone number from the JWT token
    current_user = get_jwt_identity()
    user_phone = current_user['phone']

    # Query the 'users' table for a user with the matching phone number
    user = Users.query.filter_by(phone=user_phone).first()

    # Check if the user exists
    if user:
        # Parse JSON body
        request_data = request.get_json()
        id_file = request_data.get('id', None)

        if id_file is not None:
            page = request_data.get('page', 1)
            per_page = 12
            query = Notes.query.filter(and_(Notes.user_id_created == user.id, Notes.file_id_created == id_file))
            posts_pagination = query.order_by(Notes.id.desc()).paginate(page=page, per_page=per_page, error_out=False)

            posts = posts_pagination.items

            # Build a list of post details to send in the response
            posts_list = [{
                'Note': query.note,
                'Date': query.created_at,
            } for query in posts]   
            response_data = {
                'posts': posts_list,
                'pagination': {
                    'current_page': page,
                    'next_page': page + 1 if posts_pagination.has_next else None,
                    'previous_page': page - 1 if posts_pagination.has_prev else None,
                    'per_page': per_page,
                    'total_posts': posts_pagination.total
                }
            }

            return jsonify(response_data)
        else:
            return jsonify({"message": "فایل مورد نظر شما مشخص نیست !"}), 404


    # If the user is not found, return an error response
    return jsonify({"message": "خطا کاربر مورد نظر یافت نشد !"}), 404

