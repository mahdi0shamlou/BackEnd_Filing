from flask import Blueprint, jsonify, request
from datetime import datetime
# -------------jwt tokens
from flask_jwt_extended import jwt_required, get_jwt_identity
# -------------
# ------------- models
from models import users as Users
from models import SaveCustomer
from models import db

savecustomer_bp = Blueprint('save_customer', __name__)

@savecustomer_bp.route('/Customer/Save', methods=['POST'])
@jwt_required()
def save_customer():
    try:
        # دریافت اطلاعات کاربر فعلی از توکن JWT
        current_user = get_jwt_identity()
        user_phone = current_user['phone']

        # پیدا کردن کاربر در دیتابیس
        user = Users.query.filter_by(phone=user_phone).first()

        if not user:
            return jsonify({"message": "User not found."}), 404

        # دریافت اطلاعات مشتری از درخواست
        request_data = request.get_json()
        customer_name = request_data.get('customer_name')
        customer_data = request_data.get('customer_data')
        phone = request_data.get('phone')
        desck = request_data.get('desck')

        # ایجاد و ذخیره رکورد مشتری جدید
        new_customer = SaveCustomer(
            user_id=user.id,
            customer_name=customer_name,
            customer_data=customer_data,
            phone=phone,
            desck=desck,
            created_at=datetime.utcnow()
        )
        db.session.add(new_customer)
        db.session.commit()

        return jsonify({"message": "Customer saved successfully."}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "An error occurred", "message": str(e)}), 500

@savecustomer_bp.route('/Customer/Edit/<int:id>', methods=['POST'])
@jwt_required()
def edit_customer(id):
    try:
        # دریافت اطلاعات کاربر فعلی از توکن JWT
        current_user = get_jwt_identity()
        user_phone = current_user['phone']

        # پیدا کردن کاربر در دیتابیس
        user = Users.query.filter_by(phone=user_phone).first()

        if not user:
            return jsonify({"message": "User not found."}), 404

        # پیدا کردن مشتری با ID مشخص شده
        customer = SaveCustomer.query.filter_by(id=id, user_id=user.id).first()

        if not customer:
            return jsonify({"message": "Customer not found."}), 404

        # دریافت داده‌های جدید از درخواست
        request_data = request.get_json()
        customer_name = request_data.get('customer_name', customer.customer_name)
        customer_data = request_data.get('customer_data', customer.customer_data)
        phone = request_data.get('phone', customer.phone)
        desck = request_data.get('desck', customer.desck)

        # ویرایش اطلاعات مشتری
        customer.customer_name = customer_name
        customer.customer_data = customer_data
        customer.phone = phone
        customer.desck = desck

        db.session.commit()

        return jsonify({"message": "Customer updated successfully."}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "An error occurred", "message": str(e)}), 500

@savecustomer_bp.route('/Customer/Delete/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_customer(id):
    try:
        # دریافت اطلاعات کاربر فعلی از توکن JWT
        current_user = get_jwt_identity()
        user_phone = current_user['phone']

        # پیدا کردن کاربر در دیتابیس
        user = Users.query.filter_by(phone=user_phone).first()

        if not user:
            return jsonify({"message": "User not found."}), 404

        # پیدا کردن مشتری با ID مشخص شده
        customer = SaveCustomer.query.filter_by(id=id, user_id=user.id).first()

        if not customer:
            return jsonify({"message": "Customer not found."}), 404

        # حذف مشتری
        db.session.delete(customer)
        db.session.commit()

        return jsonify({"message": "Customer deleted successfully."}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "An error occurred", "message": str(e)}), 500

@savecustomer_bp.route('/Customer/List', methods=['GET'])
@jwt_required()
def list_customers():
    try:
        # دریافت اطلاعات کاربر فعلی از توکن JWT
        current_user = get_jwt_identity()
        user_phone = current_user['phone']

        # پیدا کردن کاربر در دیتابیس
        user = Users.query.filter_by(phone=user_phone).first()

        if not user:
            return jsonify({"message": "User not found."}), 404

        # بازیابی مشتریان مرتبط با کاربر
        customers = SaveCustomer.query.filter_by(user_id=user.id).all()

        customer_list = []
        for customer in customers:
            customer_list.append({
                "id": customer.id,
                "customer_name": customer.customer_name,
                "customer_data": customer.customer_data,
                "phone": customer.phone,
                "desck": customer.desck,
                "created_at": customer.created_at,
                "updated_at": customer.updated_at
            })

        return jsonify({"customers": customer_list}), 200

    except Exception as e:
        return jsonify({"error": "An error occurred", "message": str(e)}), 500
