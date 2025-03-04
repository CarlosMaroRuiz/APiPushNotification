import logging
from bson import ObjectId
from core.database import get_db
from features.orders.models import Order

logger = logging.getLogger(__name__)

def get_courier_orders(courier_id, status=None, limit=10, skip=0):
    """
    Obtiene los pedidos de un repartidor, con filtro opcional por estado.
    
    Args:
        courier_id (str): ID del repartidor.
        status (str, optional): Estado de los pedidos a filtrar.
        limit (int, optional): Límite de resultados. Por defecto 10.
        skip (int, optional): Número de resultados a saltar (para paginación).
    
    Returns:
        dict: Diccionario con lista de pedidos y metadatos de paginación.
    """
    try:
        db = get_db()
        
       
        courier_id_obj = ObjectId(courier_id)
        
        
        query = {"courier_id": courier_id_obj}
        if status and status in [Order.STATUS_PROCESSING, Order.STATUS_COMPLETED]:
            query["status"] = status
 
        orders = db.orders.find(query).sort("created_at", -1).skip(skip).limit(limit)
        
        # Serializar resultados
        result = [Order.serialize_for_api(order) for order in orders]
        
        # Obtener el total de pedidos para esta consulta (sin límites)
        total_count = db.orders.count_documents(query)
        
        # Construir respuesta con metadatos
        response = {
            "orders": result,
            "metadata": {
                "total": total_count,
                "limit": limit,
                "skip": skip,
                "has_more": (skip + limit) < total_count
            }
        }
        
        return response
    
    except Exception as e:
        logger.error(f"Error al obtener pedidos del repartidor: {str(e)}")
        return {"orders": [], "metadata": {"total": 0, "limit": limit, "skip": skip, "has_more": False}}