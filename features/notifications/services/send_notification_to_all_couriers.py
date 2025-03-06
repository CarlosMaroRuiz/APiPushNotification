import logging
from datetime import datetime
from core.database import get_db
from features.notifications.models import Notification
from core.firebase_admin import send_multicast_notification, send_notifications_individually

logger = logging.getLogger(__name__)

def send_notification_to_all_couriers(title, body, data=None, notification_type="general", related_id=None):
    """
    Envía una notificación a todos los repartidores disponibles.
    
    Args:
        title (str): Título de la notificación.
        body (str): Contenido de la notificación.
        data (dict, optional): Datos adicionales.
        notification_type (str, optional): Tipo de notificación.
        related_id (str, optional): ID relacionado (ej. ID de pedido).
    
    Returns:
        int: Número de repartidores notificados.
    """
    try:
        db = get_db()
        
        # Obtener todos los repartidores disponibles con token FCM válido
        couriers = list(db.couriers.find({
            "available": True,
            "active": True,
            "fcm_token": {"$ne": None}
        }))
        
        # Filtrar repartidores y obtener tokens e IDs
        courier_tokens = []
        courier_ids = []
        
        for courier in couriers:
            if courier.get("fcm_token"):
                courier_tokens.append(courier.get("fcm_token"))
                courier_ids.append(courier["_id"])
        
        logger.info(f"Found {len(courier_tokens)} available couriers with FCM tokens")
        
        if not courier_tokens:
            logger.warning("No hay repartidores disponibles con token FCM válido")
            return 0
        
        # Preparar datos para la notificación
        notification_data = data or {}
        notification_data["type"] = notification_type
        if related_id:
            notification_data["related_id"] = str(related_id)
        
        # Primero intentamos con multicast
        response = None
        try:
            response = send_multicast_notification(courier_tokens, title, body, notification_data)
        except Exception as e:
            logger.warning(f"Error al enviar notificación multicast: {str(e)}")
            logger.info("Intentando enviar notificaciones individualmente...")
            response = send_notifications_individually(courier_tokens, title, body, notification_data)
            
        if not response:
            logger.warning("Error al enviar notificaciones")
            return 0
        
        # Crear notificaciones en la base de datos para cada repartidor
        now = datetime.utcnow()
        notifications = []
        
        for courier_id in courier_ids:
            notification = {
                "user_id": courier_id,
                "role": Notification.ROLE_COURIER,
                "title": title,
                "body": body,
                "data": notification_data,
                "type": notification_type,
                "related_id": related_id,
                "read": False,
                "created_at": now
            }
            notifications.append(notification)
        
        # Insertar notificaciones en la base de datos (inserción masiva)
        if notifications:
            db.notifications.insert_many(notifications)
        
        success_count = getattr(response, 'success_count', 0)
        logger.info(f"Notificación enviada correctamente a {success_count} repartidores")
        return success_count
    
    except Exception as e:
        logger.error(f"Error al enviar notificación a todos los repartidores: {str(e)}")
        return 0