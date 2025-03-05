import logging
from bson import ObjectId
from datetime import datetime, timedelta
from core.database import get_db
from features.orders.models import Order


logger = logging.getLogger(__name__)

def get_courier_history(courier_id, start_date=None, end_date=None, limit=20, skip=0):
    """
    Obtiene el historial de pedidos de un repartidor en un período de tiempo.
    
    Args:
        courier_id (str): ID del repartidor.
        start_date (str, optional): Fecha de inicio en formato ISO (YYYY-MM-DD).
        end_date (str, optional): Fecha de fin en formato ISO (YYYY-MM-DD).
        limit (int, optional): Límite de resultados. Por defecto 20.
        skip (int, optional): Número de resultados a saltar (para paginación).
    
    Returns:
        dict: Diccionario con lista de pedidos y metadatos de paginación.
    """
    try:
        db = get_db()
        
        # Convertir string a ObjectId
        courier_id_obj = ObjectId(courier_id)
        
        # Construir filtro básico para pedidos del repartidor
        query = {
            "courier_id": courier_id_obj,
            "status": Order.STATUS_COMPLETED  # Solo pedidos completados en el historial
        }
        
        # Agregar filtros de fecha si se proporcionan
        if start_date or end_date:
            date_filter = {}
            
            if start_date:
                try:
                    start_date_obj = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
                    date_filter["$gte"] = start_date_obj
                except ValueError:
                    logger.warning(f"Formato de fecha de inicio inválido: {start_date}")
            
            if end_date:
                try:
                    # Establecer el final del día para la fecha final
                    end_date_obj = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
                    end_date_obj = end_date_obj + timedelta(days=1, microseconds=-1)
                    date_filter["$lte"] = end_date_obj
                except ValueError:
                    logger.warning(f"Formato de fecha de fin inválido: {end_date}")
            
            if date_filter:
                query["completed_at"] = date_filter
        
        # Ejecutar consulta con agregación para obtener estadísticas
        pipeline = [
            {"$match": query},
            {"$sort": {"completed_at": -1}},
            {"$skip": skip},
            {"$limit": limit},
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
                    "assignment_duration_minutes": {
                        "$divide": [
                            {"$subtract": ["$assigned_at", "$created_at"]},
                            60000  # Convertir ms a minutos
                        ]
                    },
                    "delivery_duration_minutes": {
                        "$divide": [
                            {"$subtract": ["$completed_at", "$assigned_at"]},
                            60000  # Convertir ms a minutos
                        ]
                    },
                    "total_duration_minutes": {
                        "$divide": [
                            {"$subtract": ["$completed_at", "$created_at"]},
                            60000  # Convertir ms a minutos
                        ]
                    }
                }
            }
        ]
        
        orders = list(db.orders.aggregate(pipeline))
        
        # Serializar resultados
        result = []
        for order in orders:
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
            
            # Redondear las duraciones a 2 decimales
            for duration_field in ['assignment_duration_minutes', 'delivery_duration_minutes', 'total_duration_minutes']:
                if duration_field in order:
                    order[duration_field] = round(order[duration_field], 2)
            
            result.append(order)
        
        # Obtener el total de pedidos para esta consulta (sin límites)
        total_count = db.orders.count_documents(query)
        
        # Obtener estadísticas adicionales
        stats_query = db.orders.aggregate([
            {"$match": query},
            {
                "$group": {
                    "_id": None,
                    "total_orders": {"$sum": 1},
                    "avg_assignment_duration": {
                        "$avg": {
                            "$divide": [
                                {"$subtract": ["$assigned_at", "$created_at"]},
                                60000  # Convertir ms a minutos
                            ]
                        }
                    },
                    "avg_delivery_duration": {
                        "$avg": {
                            "$divide": [
                                {"$subtract": ["$completed_at", "$assigned_at"]},
                                60000  # Convertir ms a minutos
                            ]
                        }
                    },
                    "avg_total_duration": {
                        "$avg": {
                            "$divide": [
                                {"$subtract": ["$completed_at", "$created_at"]},
                                60000  # Convertir ms a minutos
                            ]
                        }
                    }
                }
            }
        ])
        
        stats = list(stats_query)
        statistics = {}
        
        if stats and len(stats) > 0:
            stats_data = stats[0]
            statistics = {
                "total_orders": stats_data.get("total_orders", 0),
                "avg_assignment_duration_minutes": round(stats_data.get("avg_assignment_duration", 0), 2),
                "avg_delivery_duration_minutes": round(stats_data.get("avg_delivery_duration", 0), 2),
                "avg_total_duration_minutes": round(stats_data.get("avg_total_duration", 0), 2)
            }
        else:
            statistics = {
                "total_orders": 0,
                "avg_assignment_duration_minutes": 0,
                "avg_delivery_duration_minutes": 0,
                "avg_total_duration_minutes": 0
            }
        
        # Construir respuesta con metadatos y estadísticas
        response = {
            "orders": result,
            "metadata": {
                "total": total_count,
                "limit": limit,
                "skip": skip,
                "has_more": (skip + limit) < total_count
            },
            "statistics": statistics
        }
        
        return response
    
    except Exception as e:
        logger.error(f"Error al obtener historial del repartidor: {str(e)}")
        return {
            "orders": [],
            "metadata": {
                "total": 0,
                "limit": limit,
                "skip": skip,
                "has_more": False
            },
            "statistics": {
                "total_orders": 0,
                "avg_assignment_duration_minutes": 0,
                "avg_delivery_duration_minutes": 0,
                "avg_total_duration_minutes": 0
            }
        }