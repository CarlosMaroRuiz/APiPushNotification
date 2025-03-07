from core.database import get_db
import logging
from werkzeug.security import check_password_hash
from datetime import datetime
from features.auth.services.generate_jwt_token import generate_jwt_token
from features.auth.models import Courier  

logger = logging.getLogger(__name__)

def login_courier(email, password, fcm_token):
    """
    Autentica a un repartidor y devuelve un token JWT.
    
    Args:
        email (str): Correo electrónico del repartidor.
        password (str): Contraseña.
        fcm_token (str): Token FCM para actualizar (obligatorio).
    
    Returns:
        tuple: (token, courier_data) o (None, None) si la autenticación falla.
    """
    # Verificar que el token FCM no sea nulo o vacío
    if not fcm_token:
        logger.error(f"Intento de login sin FCM token para repartidor: {email}")
        return None, None
        
    try:
        db = get_db()
        
        # Buscar repartidor
        courier = db.couriers.find_one({"email": email})
        
        if not courier or not check_password_hash(courier['password_hash'], password):
            logger.warning(f"Intento de login fallido para repartidor: {email}")
            return None, None
        
        # Actualizar token FCM y fecha de último login
        db.couriers.update_one(
            {"_id": courier['_id']},
            {
                "$set": {
                    "fcm_token": fcm_token,
                    "updated_at": datetime.utcnow(),
                    "last_login": datetime.utcnow()
                }
            }
        )
        
        # Actualizar datos en el objeto courier antes de serializarlo
        courier['fcm_token'] = fcm_token
        courier['last_login'] = datetime.utcnow()
        courier['updated_at'] = datetime.utcnow()
        
        # Generar token JWT
        token = generate_jwt_token(str(courier['_id']), 'courier')
        
        # Serializar datos del courier para la API
        courier_data = Courier.serialize_for_api(courier)
        
        logger.info(f"Repartidor autenticado: {email}")
        return token, courier_data
    except Exception as e:
        logger.error(f"Error en login_courier: {str(e)}")
        return None, None