from flask import Blueprint, jsonify, request
from datetime import datetime, timedelta
# -------------jwt tokens
from flask_jwt_extended import jwt_required, get_jwt_identity
# -------------
# ------------- models
from models import users as Users
from models import SearchFilter
from models import db


savefilter_bp = Blueprint('savefilter', __name__)

@savefilter_bp.route('/Search/SaveFilter', methods=['POST'])
@jwt_required()
def save_search_filter():
    try:
        # دریافت اطلاعات کاربر فعلی از توکن JWT
        current_user = get_jwt_identity()
        user_phone = current_user['phone']

        # پیدا کردن کاربر در دیتابیس
        user = Users.query.filter_by(phone=user_phone).first()

        # Get the filters from the request body
        request_data = request.get_json()
        filters = request_data.get('filters')
        filter_name = request_data.get('filter_name')

        if not filters:
            return jsonify({"message": "Filters are required."}), 400

        # Create and save the search filter record
        new_filter = SearchFilter(user_id=user.id, filters=filters, filter_name=filter_name)
        db.session.add(new_filter)
        db.session.commit()

        return jsonify({"message": "Search filter saved successfully."}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "An error occurred", "message": str(e)}), 500


@savefilter_bp.route('/Search/GetFilters', methods=['GET'])
@jwt_required()
def get_search_filters():
    try:
        # دریافت اطلاعات کاربر فعلی از توکن JWT
        current_user = get_jwt_identity()
        user_phone = current_user['phone']

        # پیدا کردن کاربر در دیتابیس
        user = Users.query.filter_by(phone=user_phone).first()

        # Retrieve all saved filters for the user
        filters = SearchFilter.query.filter_by(user_id=user.id).all()

        if not filters:
            return jsonify({"message": "No saved filters found."}), 404

        # Prepare the response data
        filters_list = [{
            'id': filter.id,
            'filters': filter.filters,
            'filter_name': filter.filter_name,
            'created_at': filter.created_at
        } for filter in filters]

        return jsonify({"filters": filters_list}), 200

    except Exception as e:
        return jsonify({"error": "An error occurred", "message": str(e)}), 500


# ------------- Delete Filter Route
@savefilter_bp.route('/Search/DeleteFilter/<int:filter_id>', methods=['DELETE'])
@jwt_required()
def delete_search_filter(filter_id):
    try:
        # دریافت اطلاعات کاربر فعلی از توکن JWT
        current_user = get_jwt_identity()
        user_phone = current_user['phone']

        # پیدا کردن کاربر در دیتابیس
        user = Users.query.filter_by(phone=user_phone).first()

        # پیدا کردن فیلتر در دیتابیس
        filter_to_delete = SearchFilter.query.filter_by(id=filter_id, user_id=user.id).first()

        if not filter_to_delete:
            return jsonify({"message": "Filter not found."}), 404

        # حذف فیلتر از دیتابیس
        db.session.delete(filter_to_delete)
        db.session.commit()

        return jsonify({"message": "Filter deleted successfully."}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "An error occurred", "message": str(e)}), 500


# ------------- Update Filter Route
@savefilter_bp.route('/Search/UpdateFilter/<int:filter_id>', methods=['PUT'])
@jwt_required()
def update_search_filter(filter_id):
    try:
        # دریافت اطلاعات کاربر فعلی از توکن JWT
        current_user = get_jwt_identity()
        user_phone = current_user['phone']

        # پیدا کردن کاربر در دیتابیس
        user = Users.query.filter_by(phone=user_phone).first()

        # پیدا کردن فیلتر در دیتابیس
        filter_to_update = SearchFilter.query.filter_by(id=filter_id, user_id=user.id).first()

        if not filter_to_update:
            return jsonify({"message": "Filter not found."}), 404

        # دریافت داده‌های جدید از درخواست
        request_data = request.get_json()
        new_filter_name = request_data.get('filter_name')
        new_filters = request_data.get('filters')

        if not new_filters:
            return jsonify({"message": "Filters are required."}), 400

        # بروزرسانی فیلتر
        filter_to_update.filter_name = new_filter_name
        filter_to_update.filters = new_filters
        filter_to_update.updated_at = datetime.utcnow()

        # ذخیره تغییرات در دیتابیس
        db.session.commit()

        return jsonify({"message": "Filter updated successfully."}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "An error occurred", "message": str(e)}), 500
