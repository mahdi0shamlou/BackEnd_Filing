from flask import request, Blueprint, jsonify
#-------------jwt tokens
from flask_jwt_extended import jwt_required, get_jwt_identity
#-------------
#------------- models
from models import users as Users
from models import Posts, UserAccess, db, ClassificationTypes, ClassificationNeighborhood
#---------------

details_bp = Blueprint('details', __name__)

def check_user_has_accses(user, mahal_id, type_id):
    user_access_ids = UserAccess.query.filter_by(user_id=user.id).with_entities(UserAccess.classifictions_id).distinct().all()

    if not user_access_ids:
        return False, [], []

    list_search = [classification[0] for classification in user_access_ids]
    # دریافت تمام type های مجاز برای این classification
    allowed_types = (db.session.query(ClassificationTypes.type)
                     .filter(ClassificationTypes.classifiction_id.in_(list_search))
                     .distinct()
                     .all())
    # Retrieve unique allowed neighborhood IDs directly
    allowed_mahal = (db.session.query(ClassificationNeighborhood.neighborhood_id)
                     .filter(ClassificationNeighborhood.classifiction_id.in_(list_search))
                     .distinct()
                     .all())

    allowed_types_flat = [classification[0] for classification in allowed_types]
    allowed_mahal_flat = [classification[0] for classification in allowed_mahal]
    print(f"this is lis of user_access {list_search}")
    print(f"mahal_id should search {mahal_id} search in {allowed_mahal_flat}")
    print(f"type_id should search {type_id} search in {allowed_types_flat}")

    # Check if mahal_id and type_id exist in the allowed lists
    if mahal_id in allowed_mahal_flat and type_id in allowed_types_flat:
        return True
    else:
        return False


@details_bp.route('/Details', methods=['POST'])
@jwt_required()
def details_file():
    try:
        # Parse JSON body
        request_data = request.get_json()

        current_user = get_jwt_identity()
        user_phone = current_user['phone']
        id_file = request_data.get('id', 1)

        user = Users.query.filter_by(phone=user_phone).first()
        auth_header = request.headers.get('Authorization', None)
        auth_header = auth_header.split(" ")[1]
        if auth_header == user.jwt_token:
            query = Posts.query.filter_by(id=id_file).first()
            check_accses = check_user_has_accses(user, query.mahal, query.type)
            if check_accses:
                try:
                    posts_list = [{
                        'id': query.id,
                        'title': query.title,
                        'Images': query.Images,
                        'city': query.city_text,
                        'type': query.type_text,
                        '_type': str(query.type)[0],
                        'price': query.price,
                        'price_two': query.price_two,
                        'PARKING': query.PARKING,
                        'CABINET': query.CABINET,
                        'ELEVATOR': query.ELEVATOR,
                        'BALCONY': query.BALCONY,
                        'Otagh': query.Otagh,
                        'Make_years': query.Make_years,
                        'phone': query.number,
                        'mahal': query.mahal_text,
                        'meter': query.meter,
                        'token': query.token,
                        'desck': query.desck,
                        'details': query.details,
                        'floor': query.floor,
                        'dwelling_units_per_floor': query.dwelling_units_per_floor,
                        'dwelling_unit_floor': query.dwelling_unit_floor,
                        'wc': query.wc,
                        'floor_type': query.floor_type,
                        'water_provider': query.water_provider,
                        'cool': query.cool,
                        'heat': query.heat,
                        'building_directions': query.building_directions,
                        'date_created_persian':query.date_created_persian,
                        'date_created': query.date_created
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
        else:
            return jsonify({'error': 'An error occurred', 'message': "شما احتمالا با چند دیوایس مختلف وارد شده اید !"}), 500
    except Exception as e:
        print(e)
        return jsonify({'error': 'مشکلی پیش اومده لطفا دوباره امتحان کنید !', 'message': str(e)}), 500


