import logging
from core.database import get_db
from features.orders.models import Order


logger = logging.getLogger(__name__)

def get_pending_orders(limit=20, skip=0):
    """
    Obtiene los pedidos pendientes disponibles para los repartidores.
    
    Args:
        limit (int, optional): Límite de resultados. Por defecto 20.
        skip (int, optional): Número de resultados a saltar (para paginación).
    
    Returns:
        dict: Diccionario con lista de pedidos pendientes y metadatos de paginación.
    """
    try:
        db = get_db()
        
        # Construir filtro para pedidos pendientes
        query = {"status": Order.STATUS_PENDING}
        
        # Ejecutar consulta
        pending_orders = db.orders.find(query).sort("created_at", 1).skip(skip).limit(limit)
        
        # Serializar resultados
        result = [Order.serialize_for_api(order) for order in pending_orders]
        
        # Obtener el total de pedidos pendientes
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
        logger.error(f"Error al obtener pedidos pendientes: {str(e)}")
        return {"orders": [], "metadata": {"total": 0, "limit": limit, "skip": skip, "has_more": False}}