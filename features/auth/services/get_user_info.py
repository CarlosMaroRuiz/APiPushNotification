from core.database import get_db
from features.auth.models import User
import logging
from bson import ObjectId
logger = logger = logging.getLogger(__name__)
def get_user_info(user_id):
    """
    Obtiene la información de un usuario por su ID.
    
    Args:
        user_id (str): ID del usuario.
    
    Returns:
        dict: Datos del usuario o None si no se encuentra.
    """
    try:
        db = get_db()
        
        # Buscar usuario por ID
        user = db.users.find_one({"_id": ObjectId(user_id)})
        
        if user:
            return User.serialize_for_api(user)
        return None
    
    except Exception as e:
        logger.error(f"Error al obtener información del usuario: {str(e)}")
        return None


