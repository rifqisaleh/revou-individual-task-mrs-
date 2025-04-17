from flask import Blueprint, request, jsonify
from app.services.auth_services import register_user, login_user, verify_user_email
from flask_jwt_extended import jwt_required

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    response, status = register_user(data)
    return jsonify(response), status

@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    response, status = login_user(data)
    return jsonify(response), status

@auth_bp.route("/verify-email", methods=["GET"])
@jwt_required()
def verify_email():
    response, status = verify_user_email()
    return jsonify(response), status

