import logging
from bson import ObjectId
from datetime import datetime
from core.database import get_db
from features.orders.models import Order
from features.auth.services import update_courier_availability
from features.notifications.services import send_user_notification


logger = logging.getLogger(__name__)

def complete_order(order_id, courier_id):
    """
    Marca un pedido como completado.
    
    Args:
        order_id (str): ID del pedido.
        courier_id (str): ID del repartidor (para verificación).
    
    Returns:
        dict: Datos del pedido actualizado o None si hay error.
    """
    try:
        db = get_db()
        
     
        order_id_obj = ObjectId(order_id)
        courier_id_obj = ObjectId(courier_id)
        
        
        order = db.orders.find_one({
            "_id": order_id_obj,
            "status": Order.STATUS_PROCESSING,
            "courier_id": courier_id_obj
        })
        
        if not order:
            logger.warning(f"Pedido {order_id} no disponible para completar por el repartidor {courier_id}")
            return None
        
  
        now = datetime.utcnow()
        result = db.orders.update_one(
            {"_id": order_id_obj, "status": Order.STATUS_PROCESSING, "courier_id": courier_id_obj},
            {
                "$set": {
                    "status": Order.STATUS_COMPLETED,
                    "completed_at": now,
                    "updated_at": now
                }
            }
        )
        
        if result.modified_count == 0:
            logger.warning(f"No se pudo completar el pedido {order_id}")
            return None
        
        # Actualizar disponibilidad del repartidor (ahora está disponible para nuevos pedidos)
        update_courier_availability(courier_id, True)
        
        # Obtener pedido actualizado
        updated_order = db.orders.find_one({"_id": order_id_obj})
        
        # Enviar notificación al usuario
        try:
            user_id = str(updated_order["user_id"])
            courier_name = updated_order.get("courier_info", {}).get("name", "El repartidor")
            
            # Título y mensaje para la notificación
            title = "Pedido completado"
            body = f"{courier_name} ha completado tu pedido"
            
            # Datos adicionales para la notificación
            notification_data = {
                "order_id": order_id,
                "type": "order_completed"
            }
            
            # Enviar notificación al usuario
            send_user_notification(
                user_id, 
                title, 
                body, 
                notification_data, 
                notification_type="order_completed", 
                related_id=order_id
            )
            
            logger.info(f"Notificación de pedido completado enviada al usuario {user_id}")
        except Exception as e:
            # Si hay un error al enviar notificaciones, continuamos y solo lo registramos
            logger.error(f"Error al enviar notificación al usuario sobre pedido completado: {str(e)}")
        
        logger.info(f"Pedido {order_id} completado por el repartidor {courier_id}")
        return Order.serialize_for_api(updated_order)
    
    except Exception as e:
        logger.error(f"Error al completar pedido: {str(e)}")
        return None