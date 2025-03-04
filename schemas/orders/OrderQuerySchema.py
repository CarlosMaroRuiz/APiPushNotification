from features.orders.models import Order
from marshmallow import Schema, fields, validate
class OrderQuerySchema(Schema):
    """
    Esquema para validar parámetros de consulta de pedidos.
    """
    status = fields.Str(validate=validate.OneOf([
        Order.STATUS_PENDING, 
        Order.STATUS_PROCESSING, 
        Order.STATUS_COMPLETED
    ]), required=False)
    limit = fields.Int(validate=validate.Range(min=1, max=100), missing=10)
    skip = fields.Int(validate=validate.Range(min=0), missing=0)
    
    class Meta:
        # Permitir campos desconocidos para flexibilidad en consultas
        unknown = 'exclude'