from flask import jsonify, g, request
import logging
from core.middleware import token_required
from schemas import validate_schema
from schemas.orders import CreateOrderSchema, OrderIdSchema, OrderQuerySchema
from features.orders.services import (
    create_order,
    assign_order,
    complete_order,
    get_order,
    get_user_orders,
    get_courier_orders,
    get_pending_orders
)

# Configurar logger
logger = logging.getLogger(__name__)

@token_required
@validate_schema(CreateOrderSchema)
def create_order_controller(validated_data):
    """
    Crea un nuevo pedido.
    
    Args:
        validated_data (dict): Datos validados del esquema.
        
    Returns:
        Response: Respuesta JSON con el resultado.
    """
    # Solo los usuarios pueden crear pedidos
    if g.role != 'user':
        return jsonify({
            "error": "Solo los usuarios pueden crear pedidos"
        }), 403
    
    result = create_order(
        str(g.user_id),
        validated_data['notes']
    )
    
    if result:
        return jsonify({
            "message": "Pedido creado correctamente",
            "order": result
        }), 201
    else:
        return jsonify({
            "error": "No se pudo crear el pedido"
        }), 400

@token_required
def get_order_controller(order_id):
    """
    Obtiene los detalles de un pedido.
    
    Args:
        order_id (str): ID del pedido.
        
    Returns:
        Response: Respuesta JSON con los detalles del pedido.
    """
    result = get_order(order_id)
    
    if not result:
        return jsonify({
            "error": "Pedido no encontrado"
        }), 404
    
    # Verificar si el usuario tiene acceso al pedido
    if g.role == 'user' and str(result.get('user_id')) != str(g.user_id):
        return jsonify({
            "error": "No tienes permiso para ver este pedido"
        }), 403
    
    # Si es repartidor, solo puede ver sus pedidos asignados o pedidos pendientes
    if g.role == 'courier' and result.get('status') != 'pending' and str(result.get('courier_id', '')) != str(g.user_id):
        return jsonify({
            "error": "No tienes permiso para ver este pedido"
        }), 403
    
    return jsonify({
        "order": result
    }), 200

@token_required
def get_orders_controller():
    """
    Obtiene los pedidos del usuario o repartidor actual.
    
    Returns:
        Response: Respuesta JSON con la lista de pedidos.
    """
    # Obtener parámetros de consulta
    status = request.args.get('status')
    limit = int(request.args.get('limit', 10))
    skip = int(request.args.get('skip', 0))
    
    if g.role == 'user':
        result = get_user_orders(str(g.user_id), status, limit, skip)
    else:  # courier
        result = get_courier_orders(str(g.user_id), status, limit, skip)
    
    return jsonify(result), 200

@token_required
def get_pending_orders_controller():
    """
    Obtiene los pedidos pendientes (solo para repartidores).
    
    Returns:
        Response: Respuesta JSON con la lista de pedidos pendientes.
    """
    # Solo los repartidores pueden ver pedidos pendientes
    if g.role != 'courier':
        return jsonify({
            "error": "Solo los repartidores pueden ver pedidos pendientes"
        }), 403
    
    # Obtener parámetros de consulta
    limit = int(request.args.get('limit', 20))
    skip = int(request.args.get('skip', 0))
    
    result = get_pending_orders(limit, skip)
    
    return jsonify(result), 200

@token_required
def assign_order_controller(order_id):
    """
    Asigna un pedido a un repartidor.
    
    Args:
        order_id (str): ID del pedido a asignar.
        
    Returns:
        Response: Respuesta JSON con el resultado.
    """
    # Solo los repartidores pueden tomar pedidos
    if g.role != 'courier':
        return jsonify({
            "error": "Solo los repartidores pueden tomar pedidos"
        }), 403
    
    result = assign_order(order_id, str(g.user_id))
    
    if result:
        return jsonify({
            "message": "Pedido asignado correctamente",
            "order": result
        }), 200
    else:
        return jsonify({
            "error": "No se pudo asignar el pedido"
        }), 400

@token_required
def complete_order_controller(order_id):
    """
    Marca un pedido como completado.
    
    Args:
        order_id (str): ID del pedido a completar.
        
    Returns:
        Response: Respuesta JSON con el resultado.
    """

    if g.role != 'courier':
        return jsonify({
            "error": "Solo los repartidores pueden completar pedidos"
        }), 403
    
    result = complete_order(order_id, str(g.user_id))
    
    if result:
        return jsonify({
            "message": "Pedido completado correctamente",
            "order": result
        }), 200
    else:
        return jsonify({
            "error": "No se pudo completar el pedido"
        }), 400