from flask import Blueprint, jsonify, request, redirect, render_template
from confige import db
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_required,
    get_jwt,
    current_user,
    get_jwt_identity,
)
from models import User, TokenBlocklist, UserInterface, Levels

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
        user = User.get_user_by_phone(phone=phone)
        if user:
            access_token = create_access_token(identity=user.username, expires_delta=False)
            data = {
            'username': "09999876739",
            'password': "0O3LH",
            'to': phone,
            'text': f"با سلام\nبه بازی میثاق خوش آمدید\n  جهت تغییر گذرواژه به لینک زیر وارد شوید:\n https://misaghgame.ir/password/reset?t={access_token}",
            'from': "", 
            'fromSupportOne': "", 
            'fromSupportTwo': ""
            }
            return jsonify({"message":"لینک بازنشانی برای شما ارسال شد", "response":post_request(url="https://rest.payamak-panel.com/api/SmartSMS/Send", payload=data)})
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
    

@auth_bp.post("/ResetPassword")
@jwt_required()
def reset_password():
    current_user.set_password(request.args.get("password"))
    db.session.commit()
    return render_template("success.html")
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

@auth_bp.post("/AnswerLeague")
@jwt_required()
def answer_league():
    
    if "GodotEngine" in request.headers.get("User-Agent"):
        data = request.get_json()
        id = current_user.data.get("last_league_level")
        if id != None:
            level = Levels.query.filter_by(id=id).first()
            if level:
                score = 0
                level_score = level.data.get("score", 0)
                state = level.data.get("state")
                user_answers = data.get("data")
                if state <= 1:
                    if state == 0:
                        answers = level.data.get("answers")
                    else:
                        answers = level.data.get("data")
                    l = []
                    words_length = 0
                    for answer in answers:
                        l2 = []
                        for t in answer:
                            if t != " ":
                                words_length += 1
                            l2.append(t)
                        l.append(l2)
                    if user_answers:
                        all_true = True
                        for x, answer in enumerate(user_answers):
                            for y, t in enumerate(answer):
                                if state == 0:
                                    z = len(answer) - y -1
                                else:
                                    z = y
                                if t == l[x][z]:
                                    if t != "":
                                      score += level_score / words_length
                                else:
                                    if l[x][z] != " ":
                                        all_true = False
                        if all_true:
                            score = level_score
                        else:
                            score = int(score)
                if state == 2:
                    if user_answers == level.data.get("correct_answer"):
                        score = level_score
                if state == 3:
                    correct_answers = []
                    for answer in level.data.get("options"):
                        if answer[1] == True:
                            correct_answers.append(answer[0])
                    for answer in user_answers:
                        if answer in correct_answers:
                            score += level_score
                        else:
                            score -= level_score
                if state == 4:
                    answers = level.data.get("answers")
                    for answer in user_answers:
                        if answer in answers:
                            score += level_score
                        else:
                            if answer != "":
                                score -= level_score
                if state == 5:
                    score = level_score
                    answers = [level.data.get("first_n"), level.data.get("last_n")]
                    first_n = []
                    last_n = []
                    for t in answers[0]:
                        first_n.append(t)
                    for t in answers[1]:
                        last_n.append(t)
                    for x, t in enumerate(user_answers[0]):
                        if t != first_n[x]:
                            score -= int(level_score / 5)
                    for x, t in enumerate(user_answers[1]):
                        if t != last_n[x]:
                            score -= int(level_score / 5)
                    if score < 0:
                        score = 0
                current_user.data = current_user.update(data={"league_score":score, "last_league_level":None}, overwrite=False)[0]
                db.session.commit()
                return jsonify({"score": current_user.data.get("league_score", 0)})
            return "مرحله وجود ندارد", 400
        return "مرحله انتخاب نشده", 400
    return "شما اجازه دسترسی ندارید", 400


@auth_bp.get("/OpenLeague")
@jwt_required()
def open_league():
    
    if "GodotEngine" in request.headers.get("User-Agent"):
        score = current_user.data.get("score")
        
        if score != None:
            league_score = UserInterface.query.first().data.get("league_score", 1500)
            if score > league_score:
                score -= league_score
                current_user.data = current_user.update(data={"score":score, "league":True, "league_score":0, "number_play":[0, 0, 0, 0, 0, 0], "played_level":[]}, overwrite=True)
                db.session.commit()
                return jsonify({"league":True})
            else:
                return jsonify({"message":"امتیاز کافی نیست"})
        else:
            return jsonify({"message":"امتیاز کافی نیست"})
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
    

