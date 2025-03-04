from core.database import get_db
import logging
from bson import ObjectId
from datetime import datetime

logger = logger = logging.getLogger(__name__)
def update_courier_availability(courier_id, available):
    """
    Actualiza la disponibilidad de un repartidor.
    
    Args:
        courier_id (str): ID del repartidor.
        available (bool): Estado de disponibilidad.
    
    Returns:
        bool: True si se actualizó correctamente, False en caso contrario.
    """
    try:
        db = get_db()
        
        # Actualizar disponibilidad
        result = db.couriers.update_one(
            {"_id": ObjectId(courier_id)},
            {"$set": {"available": available, "updated_at": datetime.utcnow()}}
        )
        
        if result.modified_count > 0:
            logger.info(f"Disponibilidad actualizada para repartidor {courier_id}: {available}")
            return True
        else:
            logger.warning(f"No se actualizó la disponibilidad para repartidor {courier_id}")
            return False
    
    except Exception as e:
        logger.error(f"Error al actualizar disponibilidad del repartidor: {str(e)}")
        return False