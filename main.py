from flask import request, jsonify, render_template, send_file, redirect
from confige import app, db, jwt
from auth import auth_bp
from users import user_bp
from models import User, UploadForm, Levels
from werkzeug.utils import secure_filename
import os
import io




jwt.init_app(app)
# register bluepints
app.register_blueprint(auth_bp, url_prefix="/auth")
app.register_blueprint(user_bp, url_prefix="/users")
 # load user
@jwt.user_lookup_loader
def user_lookup_callback(_jwt_headers, jwt_data):
    identity = jwt_data["sub"]

    return User.query.filter_by(username=identity).one_or_none()


@app.route('/download/<filename>', methods=['GET'])
def get_file(filename):
    path = filename
    if path:
        if os.path.exists(os.path.join(os.path.abspath(os.path.dirname(__file__)), app.config["UPLOAD_FOLDER"], path)):
            file_loaded = []
            
            if len((os.path.join(os.path.abspath(os.path.dirname(__file__)), app.config["UPLOAD_FOLDER"], path)).split(".")) == 2:
                with open(os.path.join(os.path.abspath(os.path.dirname(__file__)), app.config["UPLOAD_FOLDER"], path), "rb") as file:
                    file_loaded = io.BytesIO(file.read())
                return send_file(file_loaded, mimetype="json/applicton")
            return  {"message":"فایل وارد شده وجود ندارد"}, 400
        else:
            return {"message":"فایل وارد شده وجود ندارد"}, 400
    
@app.route('/ListFiles', methods=['GET'])
def get_files():
    path = request.args.get("path")
    if path:
        if os.path.exists(os.path.join(os.path.abspath(os.path.dirname(__file__)), app.config["UPLOAD_FOLDER"], path)) :
            return jsonify({"files": os.listdir(os.path.join(os.path.abspath(os.path.dirname(__file__)), app.config["UPLOAD_FOLDER"], path))})
        else:
            return {"message":"مسیر وارد شده وجود ندارد"}, 400
    else:
        return jsonify({"files": os.listdir(os.path.join(os.path.abspath(os.path.dirname(__file__)), app.config["UPLOAD_FOLDER"]))})
@app.route('/create/level', methods=['POST'])
def create_level():
    data = request.get_json()
    type = request.args.get("type", "کاوش در منطقه")
    part = request.args.get("part", "شاهین شهر و میمه")
    level = request.args.get("level", 1, int)
    if Levels().get_data(type=type, part=part, level=level):
        return redirect(f"/update/level?type={type}&part={part}&level={level}")
    new_level = Levels(type=type, part=part, level=level, data=data)
    db.session.add(new_level)
    db.session.commit()
    return jsonify({"message" : "مرحله با موفقیت ساخته شد"}), 201
@app.route('/update/level', methods=['POST', 'PATCH'])
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
    return render_template("styles.css")

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)