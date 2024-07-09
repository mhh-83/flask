from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt, current_user
from models import User
from schemas import UserSchema



user_bp = Blueprint("users", __name__)

@user_bp.get("/me")
@jwt_required()
def get_me():
    if "GodotEngine" in request.headers.get("User-Agent"):
        sort = request.args.get("sort")
        if sort == "l":
            sort = "league_score"
        if sort and sort != "":
            users = User.query.all()
            u = []
            u2 = []
            u6 = []
            for user in users:
                if sort and sort != "" and user.data.get(sort):
                    u6.append(user)
                else:
                    if not sort or sort == "":
                        u6.append(user)
            for x, user in enumerate(u6):
                u2.append(user.data.get(sort))
                u.append([x, user.data.get(sort)])
            u2.sort(reverse=True)
            u3 = []
            for x in u2:
                for y in u:
                    if y[1] == x:
                        u3.append(y)
            u4 = []
            for user in u3:
                u4.append(u6[user[0]])
            
            if current_user.data.get(sort):
                for x, user in enumerate(u4):
                    if user == current_user:
                        return jsonify({"message": "موقعیت شما طبق این رتبه بندی به شرح پیوست است", "pos":x+1, "user": current_user.username})
            else:
                return jsonify({"message": "شما در این رتبه بندی وجود ندارید", "pos":0})
            
            
        return jsonify({"message": "لطفا پارامتر را مشخص کنید", "error":"sort=?"}), 400
    return "شما اجازه دسترسی ندارید", 400
    
@user_bp.get("/all")
@jwt_required()
def get_all_users():
    if "GodotEngine" in request.headers.get("User-Agent"):
        claims = get_jwt()

        filter_data = []
        if request.args.get("filter"):
            filter_data =  request.args.get("filter").split("AND")
        sort = request.args.get("sort")
        if sort == "l":
            sort = "league_score"
        page = request.args.get("page", default=1, type=int)

        per_page = request.args.get("per_page", default=3, type=int)

        users = User.query.all()
        u = []
        for user in users:
            if sort and sort != "" and user.data.get(sort):
                u.append(user)
            else:
                if not sort or sort == "":
                    u.append(user)
        
        if sort and sort != "":
            u3 = []
            u4 = []
            for x, user in enumerate(u):
                u4.append(user.data.get(sort))
                u3.append([x, user.data.get(sort)])
            u4.sort(reverse=True)
            u5 = []
            for x in u4:
                for y in u3:
                    if y[1] == x:
                        u5.append(y)
            u6 = []
            for user in u5:
                u6.append(u[user[0]])
        else:
            u6 = u
        u2 = []
        for x, user in enumerate(u6):
            if x >= (page - 1) * per_page and x < page * per_page:
                u2.append(user)
        if filter_data:
            for user in u2:
                d = {}
                for key in filter_data:
                    if user.data.get(key):
                        d[key] = user.data.get(key)
                user.data = d
        
        result = UserSchema().dump(u2, many=True)

        return (
            jsonify(
                {
                    "users": result,
                }
            ),
            200,
        )
    return "شما اجازه دسترسی ندارید", 400

    