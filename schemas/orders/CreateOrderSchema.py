from marshmallow import Schema, fields, validate

class CreateOrderSchema(Schema):
    """
    Esquema para validar datos de creación de pedido.
    """
    notes = fields.Str(required=True, validate=validate.Length(min=5, max=500), 
                      error_messages={"required": "Las notas del pedido son obligatorias"})
