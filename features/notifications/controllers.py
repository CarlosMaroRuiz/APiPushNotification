from flask import jsonify, g, request
import logging
from core.middleware import token_required
from schemas import validate_schema
from schemas.notification_schemas import (
    NotificationIdSchema,
    NotificationQuerySchema,
    MarkAsReadSchema
)
from features.notifications.services import (
    get_user_notifications,
    get_courier_notifications,
    mark_notification_as_read,
    mark_all_notifications_as_read
)


logger = logging.getLogger(__name__)  

@token_required
@validate_schema(NotificationQuerySchema)
def get_notifications_controller(validated_data):
    """
    Obtiene las notificaciones del usuario o repartidor autenticado.
    
    Args:
        validated_data (dict): Datos validados del esquema.
        
    Returns:
        Response: Respuesta JSON con la lista de notificaciones.
    """
    # Obtener parámetros validados
    limit = validated_data.get('limit', 20)
    skip = validated_data.get('skip', 0)
    unread_only = validated_data.get('unread_only', False)
    
    if g.role == 'user':
        result = get_user_notifications(str(g.user_id), limit, skip, unread_only)
    else:  # courier
        result = get_courier_notifications(str(g.user_id), limit, skip, unread_only)
    
    return jsonify(result), 200

@token_required
def get_unread_count_controller():
    """
    Obtiene el número de notificaciones no leídas.
    
    Returns:
        Response: Respuesta JSON con el conteo de notificaciones no leídas.
    """
    if g.role == 'user':
        result = get_user_notifications(str(g.user_id), limit=1, skip=0, unread_only=True)
    else:  
        result = get_courier_notifications(str(g.user_id), limit=1, skip=0, unread_only=True)
    
    return jsonify({
        "unread_count": result["metadata"]["unread"]
    }), 200

@token_required
@validate_schema(MarkAsReadSchema)
def mark_notification_as_read_controller(validated_data):
    """
    Marca una notificación como leída.
    
    Args:
        validated_data (dict): Datos validados del esquema.
        
    Returns:
        Response: Respuesta JSON con el resultado.
    """
    notification_id = validated_data['notification_id']
    result = mark_notification_as_read(notification_id, str(g.user_id), g.role)
    
    if result:
        return jsonify({
            "message": "Notificación marcada como leída correctamente"
        }), 200
    else:
        return jsonify({
            "error": "No se pudo marcar la notificación como leída"
        }), 400

@token_required
def mark_all_notifications_as_read_controller():
    """
    Marca todas las notificaciones del usuario o repartidor como leídas.
    
    Returns:
        Response: Respuesta JSON con el resultado.
    """
    count = mark_all_notifications_as_read(str(g.user_id), g.role)
    
    return jsonify({
        "message": f"Se marcaron {count} notificaciones como leídas",
        "count": count
    }), 200