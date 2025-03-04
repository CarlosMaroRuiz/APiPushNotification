import logging
from bson import ObjectId
from core.database import get_db


logger = logging.getLogger(__name__)

def mark_notification_as_read(notification_id, user_id, role):
    """
    Marca una notificación como leída.
    
    Args:
        notification_id (str): ID de la notificación.
        user_id (str): ID del usuario o repartidor (para verificación).
        role (str): Rol ('user' o 'courier').
    
    Returns:
        bool: True si se marcó como leída, False en caso contrario.
    """
    try:
        db = get_db()
        
    
        notification_id_obj = ObjectId(notification_id)
        user_id_obj = ObjectId(user_id)
        
        # Verificar que la notificación exista y pertenezca al usuario/repartidor
        notification = db.notifications.find_one({
            "_id": notification_id_obj,
            "user_id": user_id_obj,
            "role": role
        })
        
        if not notification:
            logger.warning(f"Notificación {notification_id} no encontrada o no pertenece al {role} {user_id}")
            return False
        
        # Si ya está marcada como leída, no hacer nada
        if notification.get("read", False):
            logger.info(f"Notificación {notification_id} ya estaba marcada como leída")
            return True
        
        # Marcar como leída
        result = db.notifications.update_one(
            {"_id": notification_id_obj},
            {"$set": {"read": True}}
        )
        
        success = result.modified_count > 0
        
        if success:
            logger.info(f"Notificación {notification_id} marcada como leída")
        else:
            logger.warning(f"No se pudo marcar la notificación {notification_id} como leída")
            
        return success
    
    except Exception as e:
        logger.error(f"Error al marcar notificación como leída: {str(e)}")
        return False