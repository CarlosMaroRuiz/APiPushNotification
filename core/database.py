from flask import current_app, g
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
import logging

logger = logging.getLogger(__name__)

def get_db():
    """
    Get the current connection to the database,
    or create a new one if it doesn't exist.
    """
    if 'db' not in g:
        try:
            mongo_client = MongoClient(current_app.config['MONGO_URI'])
            mongo_client.admin.command('ismaster')
            
            #Esto guarda el cliente y base de datos en el contexto de la aplicacion
            g.mongo_client = mongo_client
            g.db = mongo_client[current_app.config['MONGO_DB_NAME']]
            
            logger.info("Conexión a MongoDB establecida correctamente")
        except ConnectionFailure as e:
            logger.error(f"No se pudo conectar a MongoDB: {e}")
            raise
    
    return g.db

def close_db(e=None):
    """
    Close the connection to the database if it is open.
    """
    mongo_client = g.pop('mongo_client', None)
    
    if mongo_client is not None:
        mongo_client.close()
        logger.info("Conexión a MongoDB cerrada")

def init_db(app):
    """
    Initializes the connection to the database and 
    registers the closing function for cleaning.
    """
    app.teardown_appcontext(close_db)
    
    # Create necessary indexes for the application
    with app.app_context():
        db = get_db()
        
        # user indexes
        db.users.create_index("email", unique=True)
        db.users.create_index("fcm_token")
        
        # deliver indexes
        db.couriers.create_index("email", unique=True)
        db.couriers.create_index("fcm_token")
        
        # order indexes
        db.orders.create_index("user_id")
        db.orders.create_index("courier_id")
        db.orders.create_index("status")
        db.orders.create_index("created_at")
        
        logger.info("Índices de MongoDB creados correctamente")