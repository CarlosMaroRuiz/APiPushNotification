from flask import jsonify, g, request
import logging
from core.middleware import token_required
from features.history.services import (
    get_user_history,
    get_courier_history,
    get_order_details
)

logger = logging.getLogger(__name__)

@token_required
def get_history_controller():
    """
    Obtiene el historial de pedidos del usuario o repartidor autenticado.
    
    Returns:
        Response: Respuesta JSON con el historial de pedidos.
    """
 
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    limit = int(request.args.get('limit', 20))
    skip = int(request.args.get('skip', 0))
    
    if g.role == 'user':
        result = get_user_history(str(g.user_id), start_date, end_date, limit, skip)
    else:  # courier
        result = get_courier_history(str(g.user_id), start_date, end_date, limit, skip)
    
    return jsonify(result), 200

@token_required
def get_order_details_controller(order_id):
    """
    Obtiene los detalles de un pedido específico del historial.
    
    Args:
        order_id (str): ID del pedido.
        
    Returns:
        Response: Respuesta JSON con los detalles del pedido.
    """
    result = get_order_details(order_id, str(g.user_id), g.role)
    
    if not result:
        return jsonify({
            "error": "Pedido no encontrado o no tienes permisos para verlo"
        }), 404
    
    return jsonify({
        "order": result
    }), 200

@token_required
def get_statistics_controller():
    """
    Obtiene estadísticas del historial de pedidos.
    
    Returns:
        Response: Respuesta JSON con estadísticas del historial.
    """

    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    if g.role == 'user':
        result = get_user_history(str(g.user_id), start_date, end_date, limit=1, skip=0)
    else:  # courier
        result = get_courier_history(str(g.user_id), start_date, end_date, limit=1, skip=0)
    
    # Devolver solo las estadísticas (sin la lista de pedidos)
    return jsonify({
        "statistics": result.get("statistics", {}),
        "total_orders": result.get("metadata", {}).get("total", 0)
    }), 200