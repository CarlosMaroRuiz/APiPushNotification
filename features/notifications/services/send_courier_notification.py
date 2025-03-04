import logging
from bson import ObjectId
from core.database import get_db
from features.notifications.models import Notification
from core.firebase_admin import send_notification


logger = logging.getLogger(__name__)

def send_courier_notification(courier_id, title, body, data=None, notification_type="general", related_id=None):
    """
    Envía una notificación a un repartidor y la guarda en la base de datos.
    
    Args:
        courier_id (str): ID del repartidor.
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
        
  
        courier_id_obj = ObjectId(courier_id)
        
        # Obtener token FCM del repartidor
        courier = db.couriers.find_one({"_id": courier_id_obj})
        
        if not courier:
            logger.error(f"Repartidor no encontrado: {courier_id}")
            return None
        

        if not courier.get("fcm_token"):
            logger.error(f"Repartidor sin token FCM: {courier_id}")
            return None
        

        notification_data = data or {}
        notification_data["type"] = notification_type
        if related_id:
            notification_data["related_id"] = related_id
        
        # Enviar notificación push a través de Firebase
        fcm_response = send_notification(
            courier["fcm_token"],
            title,
            body,
            notification_data
        )
        
        if not fcm_response:
            logger.warning(f"No se pudo enviar notificación push al repartidor: {courier_id}")

        
 
        notification = Notification(
            user_id=courier_id_obj,
            role=Notification.ROLE_COURIER,
            title=title,
            body=body,
            data=notification_data,
            notification_type=notification_type,
            related_id=related_id
        )
        

        result = db.notifications.insert_one(notification.to_dict())
        notification_id = result.inserted_id
        

        saved_notification = db.notifications.find_one({"_id": notification_id})
        
        logger.info(f"Notificación enviada y guardada para el repartidor {courier_id}: {notification_id}")
        return Notification.serialize_for_api(saved_notification)
    
    except Exception as e:
        logger.error(f"Error al enviar notificación al repartidor: {str(e)}")
        return None