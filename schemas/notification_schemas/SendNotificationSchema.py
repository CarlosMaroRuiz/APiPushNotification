from marshmallow import Schema, fields, validate

class SendNotificationSchema(Schema):
    """
    Esquema para validar datos para envío de notificación.
    """
    title = fields.Str(required=True, validate=validate.Length(min=3, max=100), 
                     error_messages={"required": "El título es obligatorio"})
    body = fields.Str(required=True, validate=validate.Length(min=3, max=1000), 
                    error_messages={"required": "El cuerpo de la notificación es obligatorio"})
    data = fields.Dict(required=False)
    notification_type = fields.Str(required=False, validate=validate.Length(max=50))
    related_id = fields.Str(required=False)