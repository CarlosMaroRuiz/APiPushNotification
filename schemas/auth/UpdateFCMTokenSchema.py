from marshmallow import Schema, fields, validates, ValidationError

class UpdateFCMTokenSchema(Schema):
    """
    Esquema para validar la actualización del token FCM.
    """
    fcm_token = fields.Str(required=True, error_messages={"required": "El token FCM es obligatorio"})
    
    @validates('fcm_token')
    def validate_fcm_token(self, value):
        # Validar que el token FCM tenga una longitud razonable
        if len(value) < 50:
            raise ValidationError("El token FCM no es válido")