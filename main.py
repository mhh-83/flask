from flask import request, jsonify, render_template, send_file
from confige import app, db
from models import User, UploadForm
from werkzeug.utils import secure_filename
import os
import io
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
    print("dafafafafa/fsfsfsfsfs/fsfs.fsf".split("."))
    
    return render_template("styles.css")
@app.route("/contacts", methods=["GET"])
def get_contacts():
    contacts = User.query.all()
    json_contacts = list(map(lambda x: x.to_json(), contacts))
    return "wellcom to our appliction"
@app.route("/get_data/<string:username>",methods=["GET"])
def get_data(username):
    data = {}
    for key in request.headers.keys():
        data[key] = request.headers[key]
    if data.get("User-Token"):
        token = data["User-Token"]
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(token):
            return user.to_json()
        return jsonify(user.check_password(token))
@app.route("/create", methods=["POST"])
def create_contact():
    username = request.json.get("username")
    password = request.json.get("password")
    
    if not username or not password:
        return (jsonify({"message": "شما باید یک نام کاربری و گذرواژه وارد کنید"}), 400)
    new_contact = User(username=username, password=password)
    try:
        db.session.add(new_contact)
        db.session.commit()
    except Exception as e:
        return (jsonify({"message":str(e)}), 400)
    
    return jsonify({"message": "کاربر ساخته شد", "token": new_contact.password}), 201
@app.route("/update/<int:user_id>", methods=["PATCH"])
def update_contact(user_id):
    contact = User.query.get(user_id)
    if not contact:
        return jsonify({"message":"کاربر وجود ندارد"}), 404
    data = request.json
    contact.username = data.get("username", contact.username)
    contact.password = data.get("password", contact.password)
    contact.email = data.get("email", contact.email)
    db.session.commit()
    return jsonify({"message": "اطلاعات کاربر بروزرسانی شد"})
@app.route("/delete/<int:user_id>", methods=["DELETE"])
def delete_contact(user_id):
    contact = User.query.get(user_id)
    if not contact:
        return jsonify({"message":"کاربر وجود ندارد"}), 404
    db.session.delete(contact)
    db.session.commit()

    return jsonify({"message": "اطلاعات کاربر حذف شد"})

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)