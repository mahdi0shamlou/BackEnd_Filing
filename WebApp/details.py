from flask import request, Blueprint, jsonify
#-------------jwt tokens
from flask_jwt_extended import jwt_required, get_jwt_identity
#-------------
#------------- models
from models import users as Users
from models import Posts
#---------------

details_bp = Blueprint('details', __name__)

def check_user_has_accses(user, mahal):
    print(user)
    print(mahal)
    return True


@details_bp.route('/Details', methods=['POST'])
@jwt_required()
def details_file():
    try:
        # Parse JSON body
        request_data = request.get_json()

        current_user = get_jwt_identity()
        user_phone = current_user['phone']

        user = Users.query.filter_by(phone=user_phone).first()
        check_accses = check_user_has_accses(user, 0)
        if check_accses:
            try:
                id_file = request_data.get('id', 1)

                query = Posts.query.filter_by(id=id_file).first()

                posts_list = [{
                    'id': query.id,
                    'title': query.title,
                    'Images': query.Images,
                    'city': query.city_text,
                    'type': query.type_text,
                    'price': query.price,
                    'price_two': query.price_two,
                    'PARKING': query.PARKING,
                    'CABINET': query.CABINET,
                    'ELEVATOR': query.ELEVATOR,
                    'Otagh': query.Otagh,
                    'Make_years': query.Make_years,
                    'phone': query.number,
                    'mahal': query.mahal_text,
                    'meter': query.meter,
                    'token': query.token,
                    'desck': query.desck,
                    'details': query.details,
                    'date_created_persian':query.date_created_persian
                }]

                response_data = {
                    'posts': posts_list,
                }


                return jsonify(response_data)
            except Exception as e:
                print(e)  # Log the error
                return jsonify({'error': 'مشکلی پیش اومده لطفا دوباره تلاش کنید !', 'message': str(e)}), 500
        else:
            return jsonify({"message": "شما به این فایل دسترسی ندارید ."}), 403

    except Exception as e:
        print(e)
        return jsonify({'error': 'مشکلی پیش اومده لطفا دوباره امتحان کنید !', 'message': str(e)}), 500

