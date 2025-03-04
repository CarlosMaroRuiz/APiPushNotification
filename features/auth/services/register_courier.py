import logging
from core.database import get_db
from werkzeug.security import generate_password_hash
from features.auth.models import Courier
logger = logging.getLogger(__name__)

def register_courier(email, name, phone, password, fcm_token):
    """
    Registra un nuevo repartidor en el sistema.
    
    Args:
        email (str): Correo electrónico del repartidor.
        name (str): Nombre del repartidor.
        phone (str): Teléfono del repartidor.
        password (str): Contraseña (sin encriptar).
        fcm_token (str): Token de Firebase Cloud Messaging (obligatorio).
    
    Returns:
        dict: Datos del repartidor creado o None si hay error.
    """
    # Verificamos que exista el token
    if not fcm_token:
        logger.error(f"Intento de registro sin FCM token para repartidor: {email}")
        return None
        
    try:
        db = get_db()
        
        # Check if the email is already registered
        if db.couriers.find_one({"email": email}):
            logger.warning(f"Intento de registro con email existente: {email}")
            return None
        
        # Encriptar contraseña
        password_hash = generate_password_hash(password)
        
        # Crear nuevo repartidor
        courier = Courier(email, name, phone, password_hash, fcm_token)
        courier_dict = courier.to_dict()
        
        # Insertar en la base de datos
        result = db.couriers.insert_one(courier_dict)
        courier_dict['_id'] = result.inserted_id
        
        logger.info(f"Repartidor registrado: {email}")
        return Courier.serialize_for_api(courier_dict)
    
    except Exception as e:
        logger.error(f"Error al registrar repartidor: {str(e)}")
        return None
