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

# Regular expression for validating notes format
def validate_note_text(text):
    # حداقل طول 1 کاراکتر و حداکثر 1000 کاراکتر
    if not 1 <= len(text) <= 1000:
        return False

    # الگوی regex برای بررسی کاراکترهای مجاز
    # اجازه حروف فارسی، انگلیسی، اعداد، فاصله و برخی علائم نگارشی
    pattern = r'^[\u0600-\u06FF\s\w\.,!؟?@#$%&*()_+=\-\[\]{}|؛:\"\']+$'

    return bool(re.match(pattern, text))


@notes_bp.route('/Notes/List', methods=['GET'])
@jwt_required()
def notes_user():
    # Get the current logged-in user's phone number from the JWT token
    current_user = get_jwt_identity()
    user_phone = current_user['phone']

    # Query the 'users' table for a user with the matching phone number
    user = Users.query.filter_by(phone=user_phone).first()

    # Check if the user exists
    if user:
        # Parse JSON body
        request_data = request.get_json()
        id_file = request_data.get('file_id', None)

        if id_file is not None:
            page = request_data.get('page', 1)
            per_page = 12
            query = Notes.query.filter(and_(Notes.user_id_created == user.id, Notes.file_id_created == id_file))
            posts_pagination = query.order_by(Notes.id.desc()).paginate(page=page, per_page=per_page, error_out=False)

            posts = posts_pagination.items

            # Build a list of post details to send in the response
            posts_list = [{
                'Note_id': query.id,
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


@notes_bp.route('/Notes/Delete', methods=['DELETE'])
@jwt_required()
def delete_note():
    # دریافت اطلاعات کاربر فعلی از توکن JWT
    current_user = get_jwt_identity()
    user_phone = current_user['phone']

    # پیدا کردن کاربر در دیتابیس
    user = Users.query.filter_by(phone=user_phone).first()

    if not user:
        return jsonify({"message": "خطا کاربر مورد نظر یافت نشد!"}), 404

    request_data = request.get_json()
    note_id = request_data.get('note_id', None)
    # پیدا کردن یادداشت مورد نظر
    note = Notes.query.filter_by(id=note_id, user_id_created=user.id).first()

    if not note:
        return jsonify({"message": "یادداشت مورد نظر یافت نشد یا شما اجازه حذف آن را ندارید!"}), 404

    try:
        # حذف یادداشت از دیتابیس
        db.session.delete(note)
        db.session.commit()
        return jsonify({"message": "یادداشت با موفقیت حذف شد"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "خطا در حذف یادداشت"}), 500


@notes_bp.route('/Notes/Create', methods=['POST'])
@jwt_required()
def create_note():
    # دریافت اطلاعات کاربر فعلی از توکن JWT
    current_user = get_jwt_identity()
    user_phone = current_user['phone']

    # پیدا کردن کاربر در دیتابیس
    user = Users.query.filter_by(phone=user_phone).first()

    if not user:
        return jsonify({"message": "خطا کاربر مورد نظر یافت نشد!"}), 404

    # دریافت داده‌های ارسالی
    data = request.get_json()

    if not data:
        return jsonify({"message": "داده‌ای دریافت نشد!"}), 400

    note_text = data.get('note')
    file_id = data.get('file_id')

    # بررسی وجود فیلدهای ضروری
    if not note_text or not file_id:
        return jsonify({"message": "لطفا تمام فیلدهای ضروری را وارد کنید!"}), 400

    # اعتبارسنجی متن نوت
    if not validate_note_text(note_text):
        return jsonify({"message": "متن نوت نامعتبر است!"}), 400

    try:
        # ایجاد نوت جدید
        new_note = Notes(
            user_id_created=user.id,
            file_id_created=file_id,
            note=note_text
        )

        db.session.add(new_note)
        db.session.commit()

        return jsonify({
            "message": "نوت با موفقیت ایجاد شد",
            "note": {
                "id": new_note.id,
                "note": new_note.note,
                "created_at": new_note.created_at
            }
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "خطا در ایجاد نوت"}), 500
