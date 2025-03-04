import logging
from bson import ObjectId
from core.database import get_db
from features.notifications.models import Notification

logger = logging.getLogger(__name__)

def get_courier_notifications(courier_id, limit=20, skip=0, unread_only=False):
    """
    Obtiene las notificaciones de un repartidor.
    
    Args:
        courier_id (str): ID del repartidor.
        limit (int, optional): Límite de resultados. Por defecto 20.
        skip (int, optional): Número de resultados a saltar (para paginación).
        unread_only (bool, optional): Solo notificaciones no leídas.
    
    Returns:
        dict: Diccionario con lista de notificaciones y metadatos de paginación.
    """
    try:
        db = get_db()
        
      
        courier_id_obj = ObjectId(courier_id)
        
     
        query = {
            "user_id": courier_id_obj,
            "role": Notification.ROLE_COURIER
        }
        
        if unread_only:
            query["read"] = False
        
        notifications = db.notifications.find(query).sort("created_at", -1).skip(skip).limit(limit)
        
   
        result = [Notification.serialize_for_api(notification) for notification in notifications]
        
    
        total_count = db.notifications.count_documents(query)
        
        # Obtener el número de notificaciones no leídas
        unread_count = db.notifications.count_documents({
            "user_id": courier_id_obj,
            "role": Notification.ROLE_COURIER,
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
        logger.error(f"Error al obtener notificaciones del repartidor: {str(e)}")
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