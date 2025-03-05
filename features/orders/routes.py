from flask import Blueprint
from features.orders.controllers import (
    create_order_controller,
    get_order_controller,
    get_orders_controller,
    get_pending_orders_controller,
    assign_order_controller,
    complete_order_controller
)


orders_bp = Blueprint('orders', __name__)

# Rutas para crear y listar pedidos
orders_bp.route('/', methods=['POST'])(create_order_controller)
orders_bp.route('/', methods=['GET'])(get_orders_controller)

# Rutas para obtener pedidos pendientes (solo repartidores)
orders_bp.route('/pending', methods=['GET'])(get_pending_orders_controller)

# Rutas para operaciones sobre un pedido específico
orders_bp.route('/<order_id>', methods=['GET'])(get_order_controller)
orders_bp.route('/<order_id>/assign', methods=['POST'])(assign_order_controller)
orders_bp.route('/<order_id>/complete', methods=['POST'])(complete_order_controller)