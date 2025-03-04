from flask import Blueprint
from features.notifications.controllers import (
    get_notifications_controller,
    get_unread_count_controller,
    mark_notification_as_read_controller,
    mark_all_notifications_as_read_controller
)

notifications_bp = Blueprint('notifications', __name__)

# Rutas para obtener notificaciones
notifications_bp.route('', methods=['GET'])(get_notifications_controller)
notifications_bp.route('/unread-count', methods=['GET'])(get_unread_count_controller)

# Rutas para marcar notificaciones como leídas
notifications_bp.route('/<notification_id>/read', methods=['POST'])(mark_notification_as_read_controller)
notifications_bp.route('/read-all', methods=['POST'])(mark_all_notifications_as_read_controller)