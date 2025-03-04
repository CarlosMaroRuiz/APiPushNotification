from features.orders.models import Order
from marshmallow import Schema, fields, validate
class OrderStatusSchema(Schema):
    """
    Esquema para validar actualizacion de estado de pedido.
    """
    status = fields.Str(required=True, validate=validate.OneOf([
        Order.STATUS_PENDING, 
        Order.STATUS_PROCESSING, 
        Order.STATUS_COMPLETED
    ]), error_messages={"required": "El estado del pedido es obligatorio"})