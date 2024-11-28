from flask import request, Blueprint, jsonify
import datetime
#-------------jwt tokens
from flask_jwt_extended import jwt_required, get_jwt_identity
from numpy.array_api import trunc

#-------------
#------------- models
from models import users as Users
from models import db
#---------------


searchenign_bp = Blueprint('searchenign', __name__)

def check_user_has_accses(user, mahal):
    print(user)
    print(mahal)
    return True

@searchenign_bp.route('/Search', methods=['POST'])
@jwt_required()
def searhc_file():
    data = request.form
    mahal = data.get('mahal')

    current_user = get_jwt_identity()
    user_phone = current_user['phone']

    # Query the 'users' table for a user with the matching phone number
    user = Users.query.filter_by(phone=user_phone).first()

    check_accses = check_user_has_accses(user, mahal)
    if check_accses:
        pass
    else:
        pass

