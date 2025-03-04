import logging
from bson import ObjectId
from datetime import datetime
from core.database import get_db
from features.orders.models import Order
from features.auth.services import get_courier_info, update_courier_availability
from features.notifications.services import send_user_notification

# Configurar logger
logger = logging.getLogger(__name__)

def assign_order(order_id, courier_id):
    """
    Asigna un pedido a un repartidor.
    
    Args:
        order_id (str): ID del pedido.
        courier_id (str): ID del repartidor.
    
    Returns:
        dict: Datos del pedido actualizado o None si hay error.
    """
    try:
        db = get_db()
        
        # Convertir IDs a ObjectId
        order_id_obj = ObjectId(order_id)
        courier_id_obj = ObjectId(courier_id)
        
        # Verificar que el pedido existe y está pendiente
        order = db.orders.find_one({
            "_id": order_id_obj,
            "status": Order.STATUS_PENDING
        })
        
        if not order:
            logger.warning(f"Pedido {order_id} no disponible para asignación")
            return None
        
        # Obtener información del repartidor
        courier_info = get_courier_info(courier_id)
        if not courier_info:
            logger.error(f"No se pudo obtener información del repartidor {courier_id}")
            return None
        
        # Incluir solo información necesaria del repartidor
        courier_data = {
            "name": courier_info.get("name", ""),
            "phone": courier_info.get("phone", ""),
            "email": courier_info.get("email", "")
        }
        
        # Actualizar el pedido
        now = datetime.utcnow()
        result = db.orders.update_one(
            {"_id": order_id_obj, "status": Order.STATUS_PENDING},
            {
                "$set": {
                    "status": Order.STATUS_PROCESSING,
                    "courier_id": courier_id_obj,
                    "courier_info": courier_data,
                    "assigned_at": now,
                    "updated_at": now
                }
            }
        )
        
        if result.modified_count == 0:
            logger.warning(f"No se pudo asignar el pedido {order_id} al repartidor {courier_id}")
            return None
        
        # Actualizar disponibilidad del repartidor en la base de datos
        # Si el repartidor ya no está disponible para más pedidos
        update_courier_availability(courier_id, False)
        
        # Obtener pedido actualizado
        updated_order = db.orders.find_one({"_id": order_id_obj})
        
        # Enviar notificación al usuario
        try:
            user_id = str(updated_order["user_id"])
            courier_name = courier_data.get("name", "Un repartidor")
            
            # Título y mensaje para la notificación
            title = "Tu pedido está en proceso"
            body = f"{courier_name} ha tomado tu pedido y está en camino"
            
            # Datos adicionales para la notificación
            notification_data = {
                "order_id": order_id,
                "type": "order_assigned",
                "courier_name": courier_name
            }
            
            # Enviar notificación al usuario
            send_user_notification(
                user_id, 
                title, 
                body, 
                notification_data, 
                notification_type="order_assigned", 
                related_id=order_id
            )
            
            logger.info(f"Notificación enviada al usuario {user_id} para el pedido {order_id}")
        except Exception as e:
            # Si hay un error al enviar notificaciones, continuamos y solo lo registramos
            logger.error(f"Error al enviar notificación al usuario: {str(e)}")
        
        logger.info(f"Pedido {order_id} asignado al repartidor {courier_id}")
        return Order.serialize_for_api(updated_order)
    
    except Exception as e:
        logger.error(f"Error al asignar pedido: {str(e)}")
        return None