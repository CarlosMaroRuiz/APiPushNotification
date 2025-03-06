import logging
from bson import ObjectId
from datetime import datetime
from core.database import get_db
from features.orders.models import Order
from features.auth.services import get_user_info
from features.notifications.services import send_notification_to_all_couriers

# Configurar logger
logger = logging.getLogger(__name__)

def create_order(user_id, notes, address):
    """
    Crea un nuevo pedido y envía notificaciones a los repartidores disponibles.
    
    Args:
        user_id (str): ID del usuario que hace el pedido.
        notes (str): Notas/descripción del pedido.
        address (str): Dirección de entrega del pedido.
    
    Returns:
        dict: Datos del pedido creado o None si hay error.
    """
    print("SSSSSSSSSSSSSSSSSSSSSSSs")
    print(notes,address)
    try:
        db = get_db()

        user_id_obj = ObjectId(user_id)
        
     
        user_info = get_user_info(user_id)
        if not user_info:
            logger.error(f"No se pudo obtener información del usuario {user_id}")
            return None
        
       
        user_data = {
            "name": user_info.get("name", ""),
            "phone": user_info.get("phone", ""),
            "email": user_info.get("email", "")
        }
        
        # Crear nuevo pedido
        order = Order(user_id_obj, notes, address, user_data)
        order_dict = order.to_dict()
        
        # Insertar en la base de datos
        result = db.orders.insert_one(order_dict)
        order_id = result.inserted_id
        order_dict['_id'] = order_id
        
        logger.info(f"Pedido creado por usuario {user_id}: {order_id}")
        
        # Enviar notificaciones a todos los repartidores disponibles
        try:
            # Título y mensaje para la notificación
            title = "Nuevo pedido disponible"
            body = f"{user_data.get('name', 'Un usuario')} ha realizado un nuevo pedido"
            
            # Datos adicionales para la notificación
            notification_data = {
                "order_id": str(order_id),
                "type": "new_order"
            }
            print("messaging")
            print(notification_data)
            # Enviar notificación a todos los repartidores disponibles
            couriers_notified = send_notification_to_all_couriers(
                title, 
                body, 
                notification_data, 
                notification_type="new_order", 
                related_id=str(order_id)
            )
            
            logger.info(f"Notificación enviada a {couriers_notified} repartidores para el pedido {order_id}")
        except Exception as e:
            # Si hay un error al enviar notificaciones, continuamos y solo lo registramos
            logger.error(f"Error al enviar notificaciones a repartidores: {str(e)}")
        
        return Order.serialize_for_api(order_dict)
    
    except Exception as e:
        logger.error(f"Error al crear pedido: {str(e)}")
        return None