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

@searchenign_bp.route('/Search', methods=['GET'])
@jwt_required()
def searhc_file():

    type_of_search = request.form.get('type', 1, type=int)
    city = request.form.get('city', 1, type=int)
    mahal = request.form.get('mahal', 1, type=int)

    current_user = get_jwt_identity()
    user_phone = current_user['phone']

    # Query the 'users' table for a user with the matching phone number
    user = Users.query.filter_by(phone=user_phone).first()

    check_accses = check_user_has_accses(user, mahal)
    if check_accses:
        return jsonify({"message": "فایلینگ"}), 200
    else:
        return jsonify({"message": "شما به این منطقه دسترسی ندارید ."}), 403
