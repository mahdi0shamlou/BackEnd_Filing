from flask import request, Blueprint, jsonify
#-------------jwt tokens
from flask_jwt_extended import jwt_required, get_jwt_identity
#-------------
#------------- models
from models import users as Users
from models import PostFileSell, PostFileRent
#---------------

searchenign_bp = Blueprint('searchenign', __name__)

def check_user_has_accses(user, mahal):
    print(user)
    print(mahal)
    return True

@searchenign_bp.route('/Search/Test', methods=['GET'])
@jwt_required()
def search_engine():
    try:
        is_sell = request.args.get('type_files', default=1, type=int)
        if is_sell == 1:
            city = request.args.get('city', default=1, type=int)
            type = request.args.get('type', default=21, type=int)
            mahals = request.args.getlist('mahal[]', type=int)  # Get list of mahal IDs
            price_from = request.args.get('price_from', type=int)
            price_to = request.args.get('price_to', type=int)
            rent_from = request.args.get('rent_from', type=int)
            rent_to = request.args.get('rent_to', type=int)
            meter_from = request.args.get('meter_from', type=int)
            meter_to = request.args.get('meter_to', type=int)
            sort_from = request.args.get('sort', 1, type=int)
            otagh = request.args.get('otagh', type=int)
            make = request.args.getlist('make[]', type=int)  # Get list of mkae years
            desck = request.args.get('desck', type=str)

            current_user = get_jwt_identity()
            user_phone = current_user['phone']

            user = Users.query.filter_by(phone=user_phone).first()

            check_accses = check_user_has_accses(user, mahals)
            if check_accses:
                return jsonify({"message": "فایلینگ"}), 200
            else:
                return jsonify({"message": "شما به این منطقه دسترسی ندارید ."}), 403

        else:
            pass
    except Exception as e:
        print(e)