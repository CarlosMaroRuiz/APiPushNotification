from marshmallow import Schema, fields, validate,validates,ValidationError
class MarkAsReadSchema(Schema):
    """
    Esquema para validar la acción de marcar una notificación como leída.
    """
    notification_id = fields.Str(required=True, error_messages={"required": "El ID de la notificación es obligatorio"})
    
    @validates('notification_id')
    def validate_notification_id(self, value):
        if not value or len(value) != 24 or not all(c in '0123456789abcdef' for c in value):
            raise ValidationError("ID de notificación no válido")