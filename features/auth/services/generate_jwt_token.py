import jwt
from datetime import datetime, timedelta
from flask import current_app

def generate_jwt_token(user_id, role):
    """
    Genera un token JWT para autenticación.
    
    Args:
        user_id (str): ID del usuario o repartidor.
        role (str): Rol ('user' o 'courier').
    
    Returns:
        str: Token JWT generado.
    """
    # Establecer tiempo de expiración
    expiration = datetime.utcnow() + timedelta(seconds=current_app.config['JWT_ACCESS_TOKEN_EXPIRES'])
  
    payload = {
        'exp': expiration,
        'iat': datetime.utcnow(),
        'user_id': user_id,
        'role': role
    }
    

    token = jwt.encode(
        payload,
        current_app.config['JWT_SECRET_KEY'],
        algorithm="HS256"
    )
    
    return token