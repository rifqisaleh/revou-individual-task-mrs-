from app.models.models import User
from app import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token
from datetime import timedelta

def register_user(data):
    username = data.get("username")
    email = data.get("email")
    password = data.get("password")
    full_name = data.get("full_name")
    role = data.get("role", "user")

    if User.query.filter((User.username == username) | (User.email == email)).first():
        return {"msg": "Username or email already exists"}, 409

    hashed_pw = generate_password_hash(password)
    new_user = User(username=username, email=email, password=hashed_pw, full_name=full_name, role=role)

    db.session.add(new_user)
    db.session.commit()

    return {"msg": "User registered successfully"}, 201


def login_user(data):
    username = data.get("username")
    password = data.get("password")

    user = User.query.filter_by(username=username).first()
    if not user or not check_password_hash(user.password, password):
        return {"msg": "Invalid username or password"}, 401

    access_token = create_access_token(
        identity={"id": user.id, "role": user.role},
        expires_delta=timedelta(hours=3)
    )

    return {"access_token": access_token}, 200
