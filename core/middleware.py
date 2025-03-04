from flask import request, jsonify, g
from flask_cors import CORS
from functools import wraps
import jwt
import logging
from core.database import get_db
from datetime import datetime
import time
from bson import ObjectId

logger = logging.getLogger(__name__)

def configure_middleware(app):
    """
    Configura el middleware necesario para la aplicación Flask.
    """
    CORS(app)
    
    # Middleware para medir tiempo de respuesta
    @app.before_request
    def start_timer():
        g.start_time = time.time()
    
    @app.after_request
    def log_request_info(response):
        # Calcular tiempo de respuesta
        if hasattr(g, 'start_time'):
            elapsed_time = time.time() - g.start_time
            logger.info(f"{request.method} {request.path} {response.status_code} - {elapsed_time:.4f}s")
        
        return response
    
    # Configurar manejador de errores
    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"error": "Recurso no encontrado"}), 404
    
    @app.errorhandler(500)
    def server_error(e):
        logger.error(f"Error interno del servidor: {str(e)}")
        return jsonify({"error": "Error interno del servidor"}), 500

def token_required(f):
    """
    Decorador para verificar el token JWT en las rutas protegidas.
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # Verificar si el token está en los headers
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            if auth_header.startswith('Bearer '):
                token = auth_header.split(' ')[1]
        
        if not token:
            return jsonify({'error': 'Token de autenticación faltante'}), 401
        
        try:
            # Decode the token
            from flask import current_app
            data = jwt.decode(token, current_app.config['JWT_SECRET_KEY'], algorithms=["HS256"])
            
            db = get_db()
            
            #we verify the role of the user
            if data['role'] == 'user':
                user = db.users.find_one({'_id': ObjectId(data['user_id'])})
                if not user:
                    return jsonify({'error': 'Usuario no encontrado'}), 401
                g.user = user
                g.role = 'user'
            elif data['role'] == 'courier':
                courier = db.couriers.find_one({'_id': ObjectId(data['user_id'])})
                if not courier:
                    return jsonify({'error': 'Repartidor no encontrado'}), 401
                g.user = courier
                g.role = 'courier'
            else:
                return jsonify({'error': 'Rol no válido'}), 401
            
            g.user_id = ObjectId(data['user_id'])
            
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token expirado. Por favor, inicie sesión nuevamente'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Token inválido'}), 401
        
        return f(*args, **kwargs)
    
    return decorated