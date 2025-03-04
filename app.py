from flask import Flask, jsonify
from core.database import init_db
from core.firebase_admin import init_firebase
from features.auth.routes import auth_bp
from features.orders.routes import orders_bp
from features.notifications.routes import notifications_bp
from core.middleware import configure_middleware
import logging
import os
from dotenv import load_dotenv


load_dotenv()

def create_app():
    """Crea y configura la aplicación Flask"""
    app = Flask(__name__)
    
    logging.basicConfig(
        level=getattr(logging, os.getenv('LOG_LEVEL', 'INFO')),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Cargar configuraciones
    app.config.from_object('config')
    
    # Inicializar Firebase Admin SDK
    init_firebase(app)
    
    # Inicializar conexión a MongoDB
    init_db(app)
    
    # Configurar middleware (CORS, autenticación, etc)
    configure_middleware(app)
    
    # Registrar blueprints
    api_prefix = app.config.get('API_PREFIX', '/api')
    app.register_blueprint(auth_bp, url_prefix=f"{api_prefix}/auth")
    app.register_blueprint(orders_bp, url_prefix=f"{api_prefix}/orders")
    app.register_blueprint(notifications_bp, url_prefix=f"{api_prefix}/notifications")
    
  
    @app.route('/')
    def index():
        return jsonify({
            "message": "Delivery App API está funcionando",
            "version": "1.0.0"
        })
    

    @app.errorhandler(404)
    def not_found(e):
        return jsonify({
            "error": "Recurso no encontrado",
            "status": 404
        }), 404
    
 
    @app.errorhandler(500)
    def server_error(e):
        app.logger.error(f"Error interno del servidor: {str(e)}")
        return jsonify({
            "error": "Error interno del servidor",
            "status": 500
        }), 500
    
    return app

if __name__ == '__main__':
    app = create_app()
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('DEBUG', 'False').lower() == 'true'
    app.logger.info(f"Iniciando servidor en el puerto {port} (DEBUG: {debug})")
    app.run(host='0.0.0.0', port=port, debug=debug)