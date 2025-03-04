import logging
from bson import ObjectId
from core.database import get_db
from features.notifications.models import Notification


logger = logging.getLogger(__name__)

def get_user_notifications(user_id, limit=20, skip=0, unread_only=False):
    """
    Obtiene las notificaciones de un usuario.
    
    Args:
        user_id (str): ID del usuario.
        limit (int, optional): Límite de resultados. Por defecto 20.
        skip (int, optional): Número de resultados a saltar (para paginación).
        unread_only (bool, optional): Solo notificaciones no leídas.
    
    Returns:
        dict: Diccionario con lista de notificaciones y metadatos de paginación.
    """
    try:
        db = get_db()
     
        user_id_obj = ObjectId(user_id)
        
 
        query = {
            "user_id": user_id_obj,
            "role": Notification.ROLE_USER
        }
        
        if unread_only:
            query["read"] = False
        
       
        notifications = db.notifications.find(query).sort("created_at", -1).skip(skip).limit(limit)
        
       
        result = [Notification.serialize_for_api(notification) for notification in notifications]
        
      
        total_count = db.notifications.count_documents(query)
        

        unread_count = db.notifications.count_documents({
            "user_id": user_id_obj,
            "role": Notification.ROLE_USER,
            "read": False
        })
        
        # Construir respuesta con metadatos
        response = {
            "notifications": result,
            "metadata": {
                "total": total_count,
                "unread": unread_count,
                "limit": limit,
                "skip": skip,
                "has_more": (skip + limit) < total_count
            }
        }
        
        return response
    
    except Exception as e:
        logger.error(f"Error al obtener notificaciones del usuario: {str(e)}")
        return {
            "notifications": [],
            "metadata": {
                "total": 0,
                "unread": 0,
                "limit": limit,
                "skip": skip,
                "has_more": False
            }
        }