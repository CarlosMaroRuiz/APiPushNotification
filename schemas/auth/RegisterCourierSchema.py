from schemas.auth.RegisterUserSchema import RegisterUserSchema

class RegisterCourierSchema(RegisterUserSchema):
    """
    Esquema para validar datos de registro de repartidor.
    Hereda del esquema de usuario.
    """
    # Mismas validaciones que el usuario por ahora