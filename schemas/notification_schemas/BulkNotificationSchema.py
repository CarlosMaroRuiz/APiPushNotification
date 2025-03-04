from marshmallow import Schema, fields, validate,validates,ValidationError
class BulkNotificationSchema(Schema):
    """
    Esquema para validar datos para envío de notificaciones a múltiples destinatarios.
    """
    user_ids = fields.List(fields.Str(), required=False)
    courier_ids = fields.List(fields.Str(), required=False)
    title = fields.Str(required=True, validate=validate.Length(min=3, max=100), 
                     error_messages={"required": "El título es obligatorio"})
    body = fields.Str(required=True, validate=validate.Length(min=3, max=1000), 
                    error_messages={"required": "El cuerpo de la notificación es obligatorio"})
    data = fields.Dict(required=False)
    notification_type = fields.Str(required=False, validate=validate.Length(max=50))
    
    @validates('user_ids')
    def validate_user_ids(self, value):
        # Validar que al menos se proporcione una lista de usuarios o repartidores
        if not hasattr(self, 'courier_ids') or not self.courier_ids:
            if not value or len(value) == 0:
                raise ValidationError("Se requiere al menos un destinatario (usuarios o repartidores)")