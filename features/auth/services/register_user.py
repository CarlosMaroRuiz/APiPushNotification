from core.database import get_db
from werkzeug.security import generate_password_hash
from features.auth.models import User
import logging


logger = logging.getLogger(__name__)

def register_user(email, name, phone, password, fcm_token):
    """
    Registra un nuevo usuario en el sistema.
    
    Args:
        email (str): Correo electrónico del usuario.
        name (str): Nombre del usuario.
        phone (str): Teléfono del usuario.
        password (str): Contraseña (sin encriptar).
        fcm_token (str): Token de Firebase Cloud Messaging (obligatorio).
    
    Returns:
        dict: Datos del usuario creado o None si hay error.
    """
    # Verificar que el token FCM no sea nulo o vacío
    if not fcm_token:
        logger.error(f"Intento de registro sin FCM token para: {email}")
        return None
        
    try:
        db = get_db()
        
        # Verificamos si el correo ya esta registrado
        if db.users.find_one({"email": email}):
            logger.warning(f"Intento de registro con email existente: {email}")
            return None
        
        # Encriptamos la contraseña
        password_hash = generate_password_hash(password)
        
        # -->Creamos un usuario
        user = User(email, name, phone, password_hash, fcm_token)
        user_dict = user.to_dict()
        #Insert one nos permite insertar solo una entidad a nuesta BD
        result = db.users.insert_one(user_dict)
        user_dict['_id'] = result.inserted_id
        
        logger.info(f"Usuario registrado: {email}")
        return User.serialize_for_api(user_dict)
    
    except Exception as e:
        logger.error(f"Error al registrar usuario: {str(e)}")
        return None