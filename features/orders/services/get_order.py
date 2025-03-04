import logging
from bson import ObjectId
from core.database import get_db
from features.orders.models import Order


logger = logging.getLogger(__name__)

def get_order(order_id):
    """
    Obtiene un pedido por su ID.
    
    Args:
        order_id (str): ID del pedido.
    
    Returns:
        dict: Datos del pedido o None si no se encuentra.
    """
    try:
        db = get_db()
        
        order_id_obj = ObjectId(order_id)
        

        order = db.orders.find_one({"_id": order_id_obj})
        
        if not order:
            logger.warning(f"Pedido no encontrado: {order_id}")
            return None
        
        return Order.serialize_for_api(order)
    
    except Exception as e:
        logger.error(f"Error al obtener pedido: {str(e)}")
        return None