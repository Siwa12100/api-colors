from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from marshmallow import Schema, fields, validate
from app.models import Color
from app.extensions import db


class ColorSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Color
        load_instance = True
        sqla_session = db.session


class ColorCreateSchema(Schema):
    name = fields.String(required=True, validate=validate.Length(min=1, max=100))
    hex_code = fields.String(required=True, validate=validate.Regexp(r"^#[0-9A-Fa-f]{6}$"))
    rgb_r = fields.Integer(required=True, validate=validate.Range(min=0, max=255))
    rgb_g = fields.Integer(required=True, validate=validate.Range(min=0, max=255))
    rgb_b = fields.Integer(required=True, validate=validate.Range(min=0, max=255))


color_schema = ColorSchema()
colors_schema = ColorSchema(many=True)
color_create_schema = ColorCreateSchema()
