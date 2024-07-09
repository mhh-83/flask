from flask import Blueprint, request, jsonify
from models import Book, db
from schemas import BookSchema
from math import ceil

book_bp = Blueprint("books", __name__)

@book_bp.post("/create")
def create():
    if "GodotEngine" in request.headers.get("User-Agent"):
        data = request.get_json()
        book = Book(name=data.get("name"), writer=data.get("writer"), link=data.get("link"), img_refrence=data.get("img_refrence"), description=data.get("description"))
        db.session.add(book)
        db.session.commit()
        return jsonify({"message":"با موفقیت ایجاد شد"})
    return "شما اجازه دسترسی ندارید", 400
@book_bp.put("/update/<id>")
def update(id:int):
    if "GodotEngine" in request.headers.get("User-Agent"):
        data = request.get_json()
        book = Book.query.filter_by(id=int(id)).first()
        if book == None:
            return jsonify({"message":"کتاب وجود ندارد"})
        book.name=data.get("name")
        book.writer=data.get("writer")
        book.link=data.get("link")
        book.img_refrence=data.get("img_refrence")
        book.description=data.get("description")
        db.session.commit()
        return jsonify({"message":"با موفقیت بروز شد"})
    return "شما اجازه دسترسی ندارید", 400

@book_bp.get("/get/<id>")
def get_book(id:int):
    if "GodotEngine" in request.headers.get("User-Agent"):
        data = {}
        book = Book.query.filter_by(id=int(id)).first()
        if book == None:
            return jsonify({"message":"کتاب وجود ندارد"})
        data["name"] = book.name
        data["writer"] = book.writer
        data["link"] = book.link
        data["img_refrence"] = book.img_refrence
        data["description"] = book.description
        return jsonify({"data": data})
    return "شما اجازه دسترسی ندارید", 400

@book_bp.delete("/delete/<id>")
def delete_book(id:int):
    if "GodotEngine" in request.headers.get("User-Agent"):
        data = {}
        book = Book.query.filter_by(id=int(id)).first()
        if book:
            db.session.delete(book)
            db.session.commit()
            return jsonify({"message": "با موفقیت حذف شد"})
        return jsonify({"message":"کتاب وجود ندارد"})
    return "شما اجازه دسترسی ندارید", 400

@book_bp.get("/all")
def get_all_books():
    if "GodotEngine" in request.headers.get("User-Agent"):
        page = request.args.get("page", default=1, type=int)
        per_page = request.args.get("per_page", default=3, type=int)
        filter = request.args.get("filter")
        books = Book.query.all()
        b2 = []
        if filter and filter != "":
            for book in books:
                if filter in book.name:
                    b2.append(book)
        else:
            b2 = books
        b = []
        for x, book in enumerate(b2):
            if x >= (page - 1) * per_page and x < page * per_page:
                b.append(book)
      
        result = BookSchema().dump(b, many=True)
        
        return (
            jsonify(
                {
                    "books": result,
                    "number_of_pages":ceil(len(b2) / per_page)
                }
            ),
            200,
        )
    return "شما اجازه دسترسی ندارید", 400

    