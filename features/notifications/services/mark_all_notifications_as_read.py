import logging
from bson import ObjectId
from core.database import get_db
from datetime import datetime


logger = logging.getLogger(__name__)

def mark_all_notifications_as_read(user_id, role):
    """
    Marca todas las notificaciones de un usuario o repartidor como leídas.
    
    Args:
        user_id (str): ID del usuario o repartidor.
        role (str): Rol ('user' o 'courier').
    
    Returns:
        int: Número de notificaciones marcadas como leídas.
    """
    try:
        db = get_db()
        
    
        user_id_obj = ObjectId(user_id)
        
        # Construir filtro para notificaciones no leídas de este usuario/repartidor
        query = {
            "user_id": user_id_obj,
            "role": role,
            "read": False
        }
        
        # Actualizar todas las notificaciones que coincidan
        result = db.notifications.update_many(
            query,
            {
                "$set": {
                    "read": True,
                    "updated_at": datetime.utcnow()
                }
            }
        )
        
        count = result.modified_count
        
        if count > 0:
            logger.info(f"Se marcaron {count} notificaciones como leídas para {role} {user_id}")
        else:
            logger.info(f"No había notificaciones sin leer para {role} {user_id}")
            
        return count
    
    except Exception as e:
        logger.error(f"Error al marcar todas las notificaciones como leídas: {str(e)}")
        return 0