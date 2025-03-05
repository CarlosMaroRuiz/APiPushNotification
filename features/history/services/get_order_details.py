import logging
from bson import ObjectId
from datetime import datetime
from core.database import get_db
from features.orders.models import Order

logger = logging.getLogger(__name__)

def get_order_details(order_id, user_id=None, role=None):
    """
    Obtiene los detalles de un pedido específico del historial, con métricas.
    
    Args:
        order_id (str): ID del pedido.
        user_id (str, optional): ID del usuario o repartidor para verificación de acceso.
        role (str, optional): Rol ('user' o 'courier') para verificación de acceso.
    
    Returns:
        dict: Datos detallados del pedido o None si no se encuentra.
    """
    try:
        db = get_db()
        
        # Convertir string a ObjectId
        order_id_obj = ObjectId(order_id)
        
        # Construir filtro básico
        query = {"_id": order_id_obj, "status": Order.STATUS_COMPLETED}
        
        # Si se proporciona usuario y rol, verificar permisos
        if user_id and role:
            user_id_obj = ObjectId(user_id)
            
            if role == 'user':
                # Verificar que el pedido pertenezca al usuario
                query["user_id"] = user_id_obj
            elif role == 'courier':
                # Verificar que el pedido haya sido atendido por el repartidor
                query["courier_id"] = user_id_obj
        
        # Ejecutar consulta con agregación para obtener métricas adicionales
        pipeline = [
            {"$match": query},
            {
                "$project": {
                    "_id": 1,
                    "user_id": 1,
                    "notes": 1,
                    "address": 1,
                    "user_info": 1,
                    "status": 1,
                    "courier_id": 1,
                    "courier_info": 1,
                    "created_at": 1,
                    "updated_at": 1,
                    "assigned_at": 1,
                    "completed_at": 1,
                    "wait_time_minutes": {
                        "$cond": {
                            "if": {"$eq": ["$assigned_at", None]},
                            "then": None,
                            "else": {
                                "$divide": [
                                    {"$subtract": ["$assigned_at", "$created_at"]},
                                    60000  # Convertir ms a minutos
                                ]
                            }
                        }
                    },
                    "delivery_time_minutes": {
                        "$cond": {
                            "if": {"$or": [
                                {"$eq": ["$assigned_at", None]},
                                {"$eq": ["$completed_at", None]}
                            ]},
                            "then": None,
                            "else": {
                                "$divide": [
                                    {"$subtract": ["$completed_at", "$assigned_at"]},
                                    60000  # Convertir ms a minutos
                                ]
                            }
                        }
                    },
                    "total_time_minutes": {
                        "$cond": {
                            "if": {"$eq": ["$completed_at", None]},
                            "then": None,
                            "else": {
                                "$divide": [
                                    {"$subtract": ["$completed_at", "$created_at"]},
                                    60000  # Convertir ms a minutos
                                ]
                            }
                        }
                    }
                }
            }
        ]
        
        # Ejecutar agregación
        orders = list(db.orders.aggregate(pipeline))
        
        # Verificar si se encontró el pedido
        if not orders or len(orders) == 0:
            logger.warning(f"Pedido no encontrado en el historial: {order_id}")
            return None
        
        # Obtener el pedido (debería ser solo uno)
        order = orders[0]
        
        # Convertir ObjectId a string
        if '_id' in order:
            order['_id'] = str(order['_id'])
        if 'user_id' in order and isinstance(order['user_id'], ObjectId):
            order['user_id'] = str(order['user_id'])
        if 'courier_id' in order and isinstance(order['courier_id'], ObjectId):
            order['courier_id'] = str(order['courier_id'])
        
        # Formatear fechas
        for date_field in ['created_at', 'updated_at', 'assigned_at', 'completed_at']:
            if date_field in order and isinstance(order[date_field], datetime):
                order[date_field] = order[date_field].isoformat()
        
        # Redondear las métricas de tiempo a 2 decimales
        for time_field in ['wait_time_minutes', 'delivery_time_minutes', 'total_time_minutes']:
            if time_field in order and order[time_field] is not None:
                order[time_field] = round(order[time_field], 2)
        
        # Obtener las notificaciones relacionadas con este pedido
        notifications = list(db.notifications.find(
            {"related_id": order_id, "role": {"$in": ["user", "courier"]}}
        ).sort("created_at", 1))
        
        # Serializar notificaciones
        notification_history = []
        for notification in notifications:
            # Eliminar campos innecesarios y formatear fechas
            notification_entry = {
                "title": notification.get("title"),
                "body": notification.get("body"),
                "type": notification.get("type"),
                "role": notification.get("role"),
                "created_at": notification.get("created_at").isoformat() if isinstance(notification.get("created_at"), datetime) else None
            }
            notification_history.append(notification_entry)
        
        # Agregar historial de notificaciones al resultado
        order["notification_history"] = notification_history
        
        return order
    
    except Exception as e:
        logger.error(f"Error al obtener detalles del pedido: {str(e)}")
        return None