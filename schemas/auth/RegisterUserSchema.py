from marshmallow import Schema, fields, validate, validates, ValidationError
import re

class RegisterUserSchema(Schema):
    """
    Esquema para validar datos de registro de usuario.
    El token FCM es obligatorio.
    """
    email = fields.Email(required=True, error_messages={"required": "El correo electrónico es obligatorio"})
    name = fields.Str(required=True, validate=validate.Length(min=3, max=100), 
                     error_messages={"required": "El nombre es obligatorio"})
    phone = fields.Str(required=True, validate=validate.Length(min=10, max=15), 
                      error_messages={"required": "El teléfono es obligatorio"})
    password = fields.Str(required=True, validate=validate.Length(min=6), 
                         error_messages={"required": "La contraseña es obligatoria"})
    fcm_token = fields.Str(required=True, error_messages={"required": "El token FCM es obligatorio"})
    
    @validates('phone')
    def validate_phone(self, value):
        # Validamos que tenga solo numero
        if not re.match(r'^\d+$', value):
            raise ValidationError("El teléfono debe contener solo números")
    
    @validates('fcm_token')
    def validate_fcm_token(self, value):
        # Validamos que el token tenga una longitud razonable
        if len(value) < 35:
            raise ValidationError("El token FCM no es válido")
