from flask import Blueprint
from features.auth.controllers import (
    register_user_controller,
    register_courier_controller,
    login_user_controller,
    login_courier_controller,
    update_fcm_token_controller,
    get_profile
)

# Creamos el blueprint
auth_bp = Blueprint('auth', __name__)

# Rutas para usuarios
auth_bp.route('/users/register', methods=['POST'])(register_user_controller)
auth_bp.route('/users/login', methods=['POST'])(login_user_controller)

# Rutas para repartidores
auth_bp.route('/couriers/register', methods=['POST'])(register_courier_controller)
auth_bp.route('/couriers/login', methods=['POST'])(login_courier_controller)

# Rutas comunes que requieren autenticación
auth_bp.route('/profile', methods=['GET'])(get_profile)
auth_bp.route('/update-fcm-token', methods=['POST'])(update_fcm_token_controller)