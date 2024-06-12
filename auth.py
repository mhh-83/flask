from flask import Blueprint, jsonify, request, redirect
from confige import db
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_required,
    get_jwt,
    current_user,
    get_jwt_identity,
)
from models import User, TokenBlocklist

auth_bp = Blueprint("auth", __name__)

import requests
from requests import JSONDecodeError
def post_request(url, method="", payload={}):
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
       
    }
    if method == "GET":
        response = requests.get(url, headers=headers)
    if method == "POST":
        response = requests.post(url, headers=headers)
    return response
@auth_bp.post("/verify")
def verify_user():
    data = request.get_json()
    user = User.get_user_by_username(username=data.get("username"))
    user_p = User.get_user_by_phone(phone=data.get("phone"))
    code = data.get("code")
    if user is not None:
        return jsonify({"error": "نام کاربری از قبل وجود دارد"}), 409
    if user_p is not None:
        return jsonify({"error": "شماره تلفن از قبل وجود دارد"}), 409
    phone :str= data.get("phone")
    if not phone.startswith("09") or len(phone) != 11:
        return jsonify({"error":"فرمت شماره نامعتبر است"})
    post_request(url=f"http://api.payamak-panel.com/post/Send.asmx?from=9850002710076739&username=09999876739&password=0O3LH&to={phone}&text=با سلام کد تائید شما :{code}", method="POST")
    return jsonify({"response":"در انتظار تائید"})
@auth_bp.post("/register")
def register_user():
    data = request.get_json()

    user = User.get_user_by_username(username=data.get("username"))
    user_p = User.get_user_by_phone(phone=data.get("phone"))

    if user is not None:
        return jsonify({"error": "نام کاربری از قبل وجود دارد"}), 409
    if user_p is not None:
        return jsonify({"error": "شماره تلفن از قبل وجود دارد"}), 409
    phone :str= data.get("phone")
    if not phone.startswith("09") or len(phone) != 11:
        return jsonify({"error":"فرمت شماره نامعتبر است"})
    new_user = User(username=data.get("username"), phone=data.get("phone"), data=data.get("data"))

    new_user.set_password(password=data.get("password"))

    new_user.save()
    return redirect(location="/auth/login")


@auth_bp.post("/login")
def login_user():
    data = request.get_json()
    if data.get("username"):
        user = User.get_user_by_username(username=data.get("username"))
    else:
        user = User.get_user_by_phone(phone=data.get("phone"))

    if user and (user.check_password(password=data.get("password"))):
        access_token = create_access_token(identity=user.username, expires_delta=False)
        refresh_token = create_refresh_token(identity=user.username)
        return (
            jsonify(
                {
                    "message": "Logged In ",
                    "tokens": {"access": access_token, "refresh": refresh_token},
                }
            ),
            200,
        )
    if data.get("username"):
        return jsonify({"error": "نام کاربری یا گذرواژه نادرست است"}), 400
    else:
        return jsonify({"error": "شماره تلفن یا گذرواژه نادرست است"}), 400


@auth_bp.get("/whoami")
@jwt_required()
def whoami():
    return jsonify(
        {
            "message": "message",
            "user_details": {
                "username": current_user.username,
                "phone": current_user.phone,
                "data":current_user.data
            },
        }
    )
@auth_bp.post("/update")
@jwt_required()
def save_data():
    data = request.get_json()
    overwrite = request.args.get("overwrite", type=int, default=1)
    change_data = data
    if overwrite:
        current_user.data = current_user.update(data, overwrite)
    else:
        d = current_user.update(data, overwrite)
      
        current_user.data = d[0]
        change_data = d[1]
    db.session.commit()
    return jsonify(
        {
        "message": "اطلاعات زیر بروزرسانی شد",
        "data":change_data
        }
    )


@auth_bp.get("/refresh")
@jwt_required(refresh=True)
def refresh_access():
    identity = get_jwt_identity()

    new_access_token = create_access_token(identity=identity)

    return jsonify({"access_token": new_access_token})


@auth_bp.get('/logout')
@jwt_required(verify_type=False) 
def logout_user():
    jwt = get_jwt()

    jti = jwt['jti']
    token_type = jwt['type']

    token_b = TokenBlocklist(jti=jti)

    token_b.save()

    return jsonify({"message": f"{token_type} token revoked successfully"}) , 200

