import logging
from core.database import get_db
from features.auth.services.generate_jwt_token import generate_jwt_token
from werkzeug.security import check_password_hash
from features.auth.models import User
from datetime import datetime
logger = logging.getLogger(__name__)
def login_user(email, password, fcm_token):
    """
    Autentica a un usuario y devuelve un token JWT.
    
    Args:
        email (str): Correo electrónico del usuario.
        password (str): Contraseña.
        fcm_token (str): Token FCM para actualizar (obligatorio).
    
    Returns:
        tuple: (token, user_data) o (None, None) si la autenticación falla.
    """
    # Verify that the FCM token exists
    if not fcm_token:
        logger.error(f"Intento de login sin FCM token para usuario: {email}")
        return None, None
        
    try:
        db = get_db()
        
        # Buscar usuario
        user = db.users.find_one({"email": email})
        if not user or not check_password_hash(user['password_hash'], password):
            logger.warning(f"Intento de login fallido para email: {email}")
            return None, None
        

        db.users.update_one(
            {"_id": user['_id']},
            {"$set": {"fcm_token": fcm_token, "updated_at": datetime.utcnow()}}
        )
        user['fcm_token'] = fcm_token
        
        # Generar token JWT
        token = generate_jwt_token(str(user['_id']), 'user')
        
        logger.info(f"Usuario autenticado: {email}")
        return token, User.serialize_for_api(user)
    
    except Exception as e:
        logger.error(f"Error en login de usuario: {str(e)}")
        return None, None
