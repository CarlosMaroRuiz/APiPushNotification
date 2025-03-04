from marshmallow import Schema, fields, validates,ValidationError
class OrderIdSchema(Schema):
    """
    Esquema para validar ID de pedido.
    """
    order_id = fields.Str(required=True, error_messages={"required": "El ID del pedido es obligatorio"})
    
    @validates('order_id')
    def validate_order_id(self, value):
        # Validar que el ID tenga el formato correcto para MongoDB ObjectId
        if not value or len(value) != 24 or not all(c in '0123456789abcdef' for c in value):
            raise ValidationError("ID de pedido no válido")