from marshmallow import fields, Schema


class UserSchema(Schema):
    id = fields.String()
    username = fields.String()
    phone = fields.String()
    data = fields.Dict()
