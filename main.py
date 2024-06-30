from flask import request, jsonify, render_template, redirect, make_response
from confige import app, db, jwt
from auth import auth_bp
from users import user_bp
from models import User, UploadForm, Levels, UserInterface
from werkzeug.utils import secure_filename
import os
from math import ceil
import bcrypt
from flask_jwt_extended import jwt_required, current_user
import random

def _filter(fil, files):
    if fil and fil != "":
        f = []
        for file in files:
            
            if len(file.split(".")) > 1 and fil in file.split(".")[0]:
                f.append(file)
        return f
    else:
        f = []
        for file in files:
            if len(file.split(".")) > 1:
                f.append(file)
        return f
   


jwt.init_app(app)
# register bluepints
app.register_blueprint(auth_bp, url_prefix="/auth")
app.register_blueprint(user_bp, url_prefix="/users")
 # load user
@jwt.user_lookup_loader
def user_lookup_callback(_jwt_headers, jwt_data):
    identity = jwt_data["sub"]
    return User.query.filter_by(username=identity).one_or_none()



    
@app.route('/ListFiles', methods=['GET'])
def get_files():
    path = request.args.get("path")
    per_page = request.args.get("per_page", default=50, type=int)
    page = request.args.get("page", default=1, type=int)
    filter = request.args.get("filter")
    if path:
        if os.path.exists(os.path.join(os.path.abspath(os.path.dirname(__file__)), app.config["UPLOAD_FOLDER"], path)) :
            files = os.listdir(os.path.join(os.path.abspath(os.path.dirname(__file__)), app.config["UPLOAD_FOLDER"], path))
            f = _filter(filter, files)
            f2 = []
            
            for x, file in enumerate(f):
                if x >= (page - 1) * per_page and x < page * per_page:
                    f2.append(f"http://misaghgame.ir/static/files/{path}/{file}")
            return jsonify({"files": f2, "number_of_page":ceil(len(f) / per_page)})
        else:
            return {"message":"مسیر وارد شده وجود ندارد"}, 400
    else:
        files = os.listdir(os.path.join(os.path.abspath(os.path.dirname(__file__)), app.config["UPLOAD_FOLDER"]))
        f2 = []
        f = _filter(filter, files)
        for x, file in enumerate(f):
            if x >= (page - 1) * per_page and x < page * per_page:
                f2.append(f"http://misaghgame.ir/static/files/{file}")
        return jsonify({"files": f2, "number_of_page":ceil(len(f) / per_page)})
    
@app.route('/levels/random', methods=['GET'])
@jwt_required()
def get_random_level():
    if current_user.data.get("number_play") == None:
        data = {"number_play":[0, 0, 0, 0, 0, 0]}
        current_user.data = current_user.update(data=data, overwrite=True)
        db.session.commit()
    if current_user.data.get("played_level") == None:
        data = {"played_level": []}
        
        current_user.data = current_user.update(data=data, overwrite=True)
        filter_data = []
        db.session.commit()
    else:
        filter_data = []
        for f in current_user.data['played_level']:
            filter_data.append(f)
        
    type = request.args.get("type", "لیگ")
    part = request.args.get("part", 0)
    
    max_play = UserInterface.query.first().data["laps_allowed"][int(part.split("type_")[1])]
    number_play = []
    for x in current_user.data["number_play"]:
        number_play.append(x)
    if len(number_play) > int(part.split("type_")[1]) and number_play[int(part.split("type_")[1])] < max_play:
        levels = Levels.query.filter_by(type=type, part=part).all()
        l = []
        for lv in levels:
            if not lv.id in filter_data:
                l.append(lv)
        max_level = len(l)
        level_content = None
        if max_level != 0:
            level = random.randint(0, max_level-1)
            level_content = l[level]
        if level_content:
            number_play[int(part.split("type_")[1])] += 1
            filter_data.append(level_content.id)
            data = {"played_level":filter_data, "number_play":number_play}
            current_user.data = current_user.update(data=data, overwrite=True)
            db.session.commit()
            return jsonify({"data": level_content.data})
        return jsonify({"message" : "مرحله وجود ندارد"}), 400
    return jsonify({"message" : "تعداد دور بیش از حد مجاز"}), 400

@app.route('/levels/get', methods=['GET'])
def get_level():
    print(request.headers)
    type = request.args.get("type", "کاوش در منطقه")
    part = request.args.get("part", "شاهین شهر و میمه")
    level = request.args.get("level", 1, int)
    level_content = Levels.query.filter_by(type=type, part=part, level=level).first()
    if level_content:
        return jsonify({"data": level_content.data})
    return jsonify({"message" : "مرحله وجود ندارد"}), 400
@app.route('/levels/max', methods=['GET'])
def get_max_level():
    type = request.args.get("type", "کاوش در منطقه")
    part = request.args.get("part", "شاهین شهر و میمه")
    level_content = Levels.query.filter_by(type=type, part=part).all()
    if level_content:
        return jsonify({"max_level": len(level_content)})
    return jsonify({"message" : "نوع مراحل یا قسمت وارد شده، وجود ندارد"}), 400
@app.route('/levels/create', methods=['POST'])
def create_level():
    data = request.get_json()
    type = request.args.get("type", "کاوش در منطقه")
    part = request.args.get("part", "شاهین شهر و میمه")
    level = request.args.get("level", 1, int)
    if Levels().get_data(type=type, part=part, level=level):
        return redirect(f"/levels/update?type={type}&part={part}&level={level}")
    new_level = Levels(type=type, part=part, level=level, data=data)
    db.session.add(new_level)
    db.session.commit()
    return jsonify({"message" : "مرحله با موفقیت ساخته شد"}), 201
@app.route('/levels/update', methods=['POST', 'PATCH'])
def update_level():
    type = request.args.get("type", "کاوش در منطقه")
    part = request.args.get("part", "شاهین شهر و میمه")
    level = request.args.get("level", 1, int)
    update = Levels().get_data(type=type, part=part, level=level)
    if update:
        update.data = request.get_json()
        db.session.commit()
        return jsonify({"message" : "مرحله با موفقیت بروز شد"}), 200
    return jsonify({"message": "مرحله وجود ندارد"}), 400
@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    form = UploadForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            file = request.files["file"]
            file.save(os.path.join(os.path.abspath(os.path.dirname(__file__)), app.config["UPLOAD_FOLDER"], secure_filename(file.filename)))
            return secure_filename(file.filename) + " uploaded!"
    else:
        return render_template("upload.html", form=form, style=render_template("styles.css"))
@app.route("/")
def home():
    response = make_response(render_template("home.html"), 200)
    return response
@app.route("/game/data", methods=["GET"])
@jwt_required()
def get_interface():
    data = UserInterface.query.first().data
    return jsonify({"data":data})


@app.route("/gamedata/create", methods=["POST"])
def create_interface():
    data = request.get_json()
    game_data = UserInterface(data=data)
    db.session.add(game_data)
    db.session.commit()
    return jsonify({"data":data})

@app.route("/gamedata/update", methods=["PUT"])
def update_interface():
    data = request.get_json()
    game_data = UserInterface.query.first()
    for key in game_data.data.keys():
        if not data.get(key):
            data[key] = game_data.data.get(key)
    game_data.data = data
    db.session.commit()
    return jsonify({"data":data})

@app.route("/gamedata/delete", methods=["DELETE"])
def delete_interface():
    id = request.args.get("id")
    game_data = UserInterface.query.all()
    for data in game_data:
        if data.id == id:
            db.session.delete(data)
    db.session.commit()
    return jsonify({"message": "با موفقیت حذف شد"})


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)



