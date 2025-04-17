from app.models.models import User
from app import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token, get_jwt_identity, get_jwt
from datetime import timedelta
import re

# Validate password strength
def is_strong_password(password):
    return (
        len(password) >= 8 and
        re.search(r"[A-Za-z]", password) and
        re.search(r"[0-9]", password)
    )

# Generate short-lived token for email verification
def generate_email_verification_token(user_id):
    return create_access_token(
        identity=str(user_id),
        expires_delta=timedelta(hours=1),
        additional_claims={"purpose": "email_verification"}
    )

def verify_user_email():
    jwt_data = get_jwt()
    if jwt_data.get("purpose") != "email_verification":
        return {"msg": "Invalid or expired token"}, 400

    user_id = get_jwt_identity()
    user = User.query.filter_by(id=user_id).first()

    if not user:
        return {"msg": "User not found"}, 404

    if user.is_verified:
        return {"msg": "Email already verified"}, 200

    user.is_verified = True
    db.session.commit()
    return {"msg": "Email verified successfully"}, 200


# Mock email sender (prints to terminal)
def send_verification_email(user, token):
    verify_url = f"http://localhost:5000/verify-email?token={token}"
    print("=" * 60)
    print(f"🔐 MOCK EMAIL to: {user.email}")
    print(f"Hello {user.full_name},")
    print("Please verify your email by clicking the link below:")
    print(f"{verify_url}")
    print("This link expires in 1 hour.")
    print("=" * 60)

# Main register function
def register_user(data):
    if not all(key in data and data[key] for key in ["username", "email", "password"]):
        return {"msg": "Missing required fields"}, 400

    username = data.get("username").strip()
    email = data.get("email").strip().lower()
    password = data.get("password")
    full_name = data.get("full_name", "").strip()
    role = data.get("role", "user")

    if not is_strong_password(password):
        return {"msg": "Password must be at least 8 characters long and include both letters and numbers"}, 400

    if User.query.filter((User.username == username) | (User.email == email)).first():
        return {"msg": "Username or email already exists"}, 409

    hashed_pw = generate_password_hash(password)
    new_user = User(
        username=username,
        email=email,
        password=hashed_pw,
        full_name=full_name,
        role=role,
        is_verified=False  # mark unverified initially
    )

    db.session.add(new_user)
    db.session.commit()

    token = generate_email_verification_token(new_user.id)
    send_verification_email(new_user, token)

    return {"msg": "User registered successfully. Please check your email to verify your account."}, 201



def login_user(data):
    username = data.get("username")
    password = data.get("password")

    user = User.query.filter_by(username=username).first()
    if not user or not check_password_hash(user.password, password):
        return {"msg": "Invalid username or password"}, 401

    access_token = create_access_token(
        identity=str(user.id),  # ✅ ID must be string
        additional_claims={"role": user.role},  # ✅ put role in custom claims
        expires_delta=timedelta(hours=3)
    )

    return {"access_token": access_token}, 200

