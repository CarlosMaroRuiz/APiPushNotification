from core.database import get_db
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

def update_fcm_token(user_id, role, fcm_token):
    """
    Actualiza el token FCM de un usuario o repartidor.
    
    Args:
        user_id (str): ID del usuario o repartidor.
        role (str): Rol ('user' o 'courier').
        fcm_token (str): Nuevo token FCM.
    
    Returns:
        bool: True si se actualizó correctamente, False en caso contrario.
    """
    # Verificar que el token FCM no sea nulo o vacío
    if not fcm_token:
        logger.error(f"Intento de actualización con FCM token vacío para {role} {user_id}")
        return False
        
    try:
        db = get_db()
        
        # Determinar la colección según el rol
        collection = db.users if role == 'user' else db.couriers
        
        # Actualizar token
        result = collection.update_one(
            {"_id": user_id},
            {"$set": {"fcm_token": fcm_token, "updated_at": datetime.utcnow()}}
        )
        
        if result.modified_count > 0:
            logger.info(f"Token FCM actualizado para {role} {user_id}")
            return True
        else:
            logger.warning(f"No se actualizó el token FCM para {role} {user_id}")
            return False
    
    except Exception as e:
        logger.error(f"Error al actualizar token FCM: {str(e)}")
        return False