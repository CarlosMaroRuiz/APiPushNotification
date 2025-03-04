from marshmallow import Schema, fields, validates, ValidationError

class LoginSchema(Schema):
    """
    Esquema para validar datos de inicio de sesión.
    El token FCM es obligatorio.
    """
    email = fields.Email(required=True, error_messages={"required": "El correo electrónico es obligatorio"})
    password = fields.Str(required=True, error_messages={"required": "La contraseña es obligatoria"})
    fcm_token = fields.Str(required=True, error_messages={"required": "El token FCM es obligatorio"})
    
    @validates('fcm_token')
    def validate_fcm_token(self, value):
        # Validar que el token FCM tenga una longitud razonable
        if len(value) < 50:
            raise ValidationError("El token FCM no es válido")