from flask import Blueprint
from features.history.controllers import (
    get_history_controller,
    get_order_details_controller,
    get_statistics_controller
)


history_bp = Blueprint('history', __name__)


history_bp.route('', methods=['GET'])(get_history_controller)
history_bp.route('/statistics', methods=['GET'])(get_statistics_controller)
history_bp.route('/orders/<order_id>', methods=['GET'])(get_order_details_controller)