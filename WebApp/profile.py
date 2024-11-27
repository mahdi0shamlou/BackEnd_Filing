from flask import request, Blueprint, jsonify
import datetime
#-------------jwt tokens
from flask_jwt_extended import jwt_required, get_jwt_identity
#-------------
#------------- models
from models import users as Users
from models import db
#---------------


profile_bp = Blueprint('profile', __name__)

@profile_bp.route('/Profile', methods=['Get'])
@jwt_required()
def profile():
    current_user = get_jwt_identity()
    user_phone = current_user['phone']
