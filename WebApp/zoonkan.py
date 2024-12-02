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

zoonkan_bp = Blueprint('zoonkan', __name__)
