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
def post_request(url, payload={}):
    headers = {
    'content-type': 'application/x-www-form-urlencoded'
    }

    requests.packages.urllib3.disable_warnings()
    session = requests.Session()
    session.verify = False

    response = session.post(url, data=payload, headers=headers)

    return (response.text)
    
@auth_bp.post("/verify")
def verify_user():
    if "GodotEngine" in request.headers.get("User-Agent"):
        data = request.get_json()
        if not data.get("username"):
            return jsonify({"error": "نام کاربری  خود را وارد کنید"}), 400
        password = data.get("password")
        if not password:
            return jsonify({"error": "گذرواژه خود را وارد کنید"}), 400
        if len(password) < 8:
            return jsonify({"error": "گذرواژه حداقل باید 8 کارکتر باشد"}), 400
        user = User.get_user_by_username(username=data.get("username"))
        user_p = User.get_user_by_phone(phone=data.get("phone"))
        code = data.get("code")
        
        if user is not None:
            return jsonify({"error": "نام کاربری از قبل وجود دارد"}), 409
        if user_p is not None:
            return jsonify({"error": "شماره تلفن از قبل وجود دارد"}), 409
        phone :str= data.get("phone")
        if not phone.startswith("09") or len(phone) != 11:
            return jsonify({"error":"فرمت شماره نامعتبر است"}), 400
        
        data = {
        'username': "09999876739",
        'password': "0O3LH",
        'to': phone,
        'text': f"با سلام\nبه بازی میثاق خوش آمدید\n کد تائید شما جهت ثبت نام در بازی :\n{code}",
        'from': "", 
        'fromSupportOne': "", 
        'fromSupportTwo': ""
        }
        
        return jsonify({"message":"در انتظار تائید", "response":post_request(url="https://rest.payamak-panel.com/api/SmartSMS/Send", payload=data)})
    return "شما اجازه دسترسی ندارید", 400
    
@auth_bp.post("/recovery")
def recovery_user():
    if "GodotEngine" in request.headers.get("User-Agent"):
        data = request.get_json()
        phone = data.get("phone")
        code = data.get("code")
        user = User.get_user_by_phone(phone=phone)
        if user:
            data = {
            'username': "09999876739",
            'password': "0O3LH",
            'to': phone,
            'text': f"با سلام\nبه بازی میثاق خوش آمدید\n  جهت تغییر گذرواژه کد زیر را وارد کنید:\n{code}",
            'from': "", 
            'fromSupportOne': "", 
            'fromSupportTwo': ""
            }
            return jsonify({"message":"در انتظار تائید", "response":post_request(url="https://rest.payamak-panel.com/api/SmartSMS/Send", payload=data)})
        else:
            return jsonify({"error":"کاربر وجود ندارد"}), 400
    return "شما اجازه دسترسی ندارید", 400
    
@auth_bp.post("/register")
def register_user():
    if "GodotEngine" in request.headers.get("User-Agent"):
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
    return "شما اجازه دسترسی ندارید", 400


@auth_bp.post("/login")
def login_user():
    if "GodotEngine" in request.headers.get("User-Agent"):
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
                        "tokens": {"access": access_token, "refresh": refresh_token, "id":user.id},
                    }
                ),
                200,
            )
        if data.get("username"):
            return jsonify({"error": "نام کاربری یا گذرواژه نادرست است"}), 400
        else:
            return jsonify({"error": "شماره تلفن یا گذرواژه نادرست است"}), 400
    return "شما اجازه دسترسی ندارید", 400
    


@auth_bp.get("/whoami")
@jwt_required()
def whoami():
    if "GodotEngine" in request.headers.get("User-Agent"):
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
    return "شما اجازه دسترسی ندارید", 400
    
@auth_bp.post("/update")
@jwt_required()
def save_data():
    if "GodotEngine" in request.headers.get("User-Agent"):
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
    return "شما اجازه دسترسی ندارید", 400
    


@auth_bp.get("/refresh")
@jwt_required(refresh=True)
def refresh_access():
    if "GodotEngine" in request.headers.get("User-Agent"):
        identity = get_jwt_identity()

        new_access_token = create_access_token(identity=identity)

        return jsonify({"access_token": new_access_token})
    return "شما اجازه دسترسی ندارید", 400
    


@auth_bp.get('/logout')
@jwt_required(verify_type=False) 
def logout_user():
    if "GodotEngine" in request.headers.get("User-Agent"):
        jwt = get_jwt()

        jti = jwt['jti']
        token_type = jwt['type']

        token_b = TokenBlocklist(jti=jti)

        token_b.save()

        return jsonify({"message": f"{token_type} token revoked successfully"}) , 200
    return "شما اجازه دسترسی ندارید", 400
    

