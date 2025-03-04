import re
import logging
from datetime import datetime
from bson import ObjectId

# Configurar logger
logger = logging.getLogger(__name__)

def validate_email(email):
    """
    Valida el formato de un correo electrónico.
    
    Args:
        email (str): Correo electrónico a validar.
    
    Returns:
        bool: True si es válido, False en caso contrario.
    """
    if not email:
        return False
    
    # Patrón básico de validación de correo
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def validate_phone(phone):
    """
    Valida el formato de un número de teléfono.
    
    Args:
        phone (str): Número de teléfono a validar.
    
    Returns:
        bool: True si es válido, False en caso contrario.
    """
    if not phone:
        return False
    
    # Solo aceptar numeros
    return bool(re.match(r'^\d+$', phone))

def validate_objectid(id_str):
    """
    Valida si una cadena tiene el formato de un ObjectId de MongoDB.
    
    Args:
        id_str (str): Cadena a validar.
    
    Returns:
        bool: True si es válido, False en caso contrario.
    """
    if not id_str:
        return False
    
    # Validar formato (24 caracteres hexadecimales)
    if not re.match(r'^[0-9a-fA-F]{24}$', id_str):
        return False
    
    # Intentar crear un ObjectId
    try:
        ObjectId(id_str)
        return True
    except:
        return False

def format_date(date):
    """
    Formatea una fecha en formato ISO.
    
    Args:
        date (datetime): Fecha a formatear.
    
    Returns:
        str: Fecha formateada o None si hay error.
    """
    if not date:
        return None
    
    try:
        if isinstance(date, str):
            # Intentar convertir de string a datetime
            date = datetime.fromisoformat(date.replace('Z', '+00:00'))
        
        return date.isoformat()
    except Exception as e:
        logger.error(f"Error al formatear fecha: {str(e)}")
        return None

def validate_fcm_token(token):
    """
    Valida si un token FCM tiene un formato válido.
    
    Args:
        token (str): Token FCM a validar.
    
    Returns:
        bool: True si es válido, False en caso contrario.
    """
    if not token or not isinstance(token, str):
        return False
    
    # Los tokens FCM suelen ser largos
    if len(token) < 50:
        return False
    
    # Verificar que solo contenga caracteres válidos
    return bool(re.match(r'^[a-zA-Z0-9:_\-]+$', token))