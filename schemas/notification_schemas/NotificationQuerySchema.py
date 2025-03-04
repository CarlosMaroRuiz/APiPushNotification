from marshmallow import Schema, fields, validate
class NotificationQuerySchema(Schema):
    """
    Esquema para validar parámetros de consulta de notificaciones.
    """
    unread_only = fields.Boolean(missing=False)
    limit = fields.Int(validate=validate.Range(min=1, max=100), missing=20)
    skip = fields.Int(validate=validate.Range(min=0), missing=0)
    
    class Meta:
        # Permitir campos desconocidos para flexibilidad en consultas
        unknown = 'exclude'