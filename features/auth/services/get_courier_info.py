from core.database import get_db
from bson import ObjectId
from features.auth.models import Courier
import logging

logger = logger = logging.getLogger(__name__)

def get_courier_info(courier_id):
    """
    Obtiene la información de un repartidor por su ID.
    
    Args:
        courier_id (str): ID del repartidor.
    
    Returns:
        dict: Datos del repartidor o None si no se encuentra.
    """
    try:
        db = get_db()
        courier = db.couriers.find_one({"_id": ObjectId(courier_id)})

        if courier:
            return Courier.serialize_for_api(courier)
        return None
    
    except Exception as e:
        logger.error(f"Error al obtener información del repartidor: {str(e)}")
        return None