import logging
from bson import ObjectId
from core.database import get_db
from features.orders.models import Order

# Configurar logger
logger = logging.getLogger(__name__)

def get_user_orders(user_id, status=None, limit=10, skip=0):
    """
    Obtiene los pedidos de un usuario, con filtro opcional por estado.
    
    Args:
        user_id (str): ID del usuario.
        status (str, optional): Estado de los pedidos a filtrar.
        limit (int, optional): Límite de resultados. Por defecto 10.
        skip (int, optional): Número de resultados a saltar (para paginación).
    
    Returns:
        list: Lista de pedidos o lista vacía si no hay resultados.
    """
    try:
        db = get_db()
        
    
        user_id_obj = ObjectId(user_id)
        
        # Construir filtro
        query = {"user_id": user_id_obj}
        if status and status in [Order.STATUS_PENDING, Order.STATUS_PROCESSING, Order.STATUS_COMPLETED]:
            query["status"] = status
        
        # Ejecutar consulta
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
        logger.error(f"Error al obtener pedidos del usuario: {str(e)}")
        return {"orders": [], "metadata": {"total": 0, "limit": limit, "skip": skip, "has_more": False}}