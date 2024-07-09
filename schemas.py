from marshmallow import fields, Schema


class UserSchema(Schema):
    id = fields.String()
    username = fields.String()
    phone = fields.String()
    data = fields.Dict()
class BookSchema(Schema):
    id = fields.String()
    link = fields.String()
    name = fields.String()
    writer = fields.String()
    description = fields.String()
    img_refrence = fields.String()
    