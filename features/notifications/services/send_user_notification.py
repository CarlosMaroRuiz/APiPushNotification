import logging
from bson import ObjectId
from core.database import get_db
from features.notifications.models import Notification
from core.firebase_admin import send_notification


logger = logging.getLogger(__name__)

def send_user_notification(user_id, title, body, data=None, notification_type="general", related_id=None):
    """
    Envía una notificación a un usuario y la guarda en la base de datos.
    
    Args:
        user_id (str): ID del usuario.
        title (str): Título de la notificación.
        body (str): Contenido de la notificación.
        data (dict, optional): Datos adicionales.
        notification_type (str, optional): Tipo de notificación.
        related_id (str, optional): ID relacionado (ej. ID de pedido).
    
    Returns:
        dict: Datos de la notificación guardada o None si hay error.
    """
    try:
        db = get_db()
        
    
        user_id_obj = ObjectId(user_id)
        
        # Obtener token FCM del usuario
        user = db.users.find_one({"_id": user_id_obj})
        
        if not user:
            logger.error(f"Usuario no encontrado: {user_id}")
            return None
        
       
        if not user.get("fcm_token"):
            logger.error(f"Usuario sin token FCM: {user_id}")
            return None
        
     
        notification_data = data or {}
        notification_data["type"] = notification_type
        if related_id:
            notification_data["related_id"] = related_id
        
        # Enviar notificación push a través de Firebase
        fcm_response = send_notification(
            user["fcm_token"],
            title,
            body,
            notification_data
        )
        
        if not fcm_response:
            logger.warning(f"No se pudo enviar notificación push al usuario: {user_id}")
            
        notification = Notification(
            user_id=user_id_obj,
            role=Notification.ROLE_USER,
            title=title,
            body=body,
            data=notification_data,
            notification_type=notification_type,
            related_id=related_id
        )
        
        # Guardar en la base de datos
        result = db.notifications.insert_one(notification.to_dict())
        notification_id = result.inserted_id
        
        # Obtener la notificación guardada
        saved_notification = db.notifications.find_one({"_id": notification_id})
        
        logger.info(f"Notificación enviada y guardada para el usuario {user_id}: {notification_id}")
        return Notification.serialize_for_api(saved_notification)
    
    except Exception as e:
        logger.error(f"Error al enviar notificación al usuario: {str(e)}")
        return None