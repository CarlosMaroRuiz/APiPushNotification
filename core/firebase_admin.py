import firebase_admin
from firebase_admin import credentials, messaging
from flask import current_app, g
import logging
import os

logger = logging.getLogger(__name__)

def get_firebase_app():
    """
   Get the Firebase application initialized or create a new one if it doesn't exist.
    """
    if 'firebase_app' not in g:
        logger.info("Inicializando Firebase Admin SDK")
        try:
            # Credential paths
            cred_path = current_app.config.get('FIREBASE_CREDENTIALS_PATH', 'deliversurimbo-firebase-adminsdk-fbsvc-e7d73aeff9.json')
            
    
            if not os.path.exists(cred_path):
                logger.error(f"Archivo de credenciales no encontrado en: {cred_path}")
                raise FileNotFoundError(f"Archivo de credenciales no encontrado: {cred_path}")
            
            # we use the credentials file
            cred = credentials.Certificate(cred_path)
            
            # Init firebase sdk
            g.firebase_app = firebase_admin.initialize_app(cred)
            logger.info("Firebase Admin SDK inicializado correctamente")
        except Exception as e:
            logger.error(f"Error al inicializar Firebase Admin SDK: {str(e)}")
            raise
    
    return g.firebase_app

def close_firebase(e=None):
    """
    Clean up Firebase resources at the end of the application.
    """
    firebase_app = g.pop('firebase_app', None)
    
    if firebase_app is not None:
        try:
            firebase_admin.delete_app(firebase_app)
            logger.info("Firebase Admin SDK finalizado")
        except Exception as e:
            logger.error(f"Error al finalizar Firebase Admin SDK: {str(e)}")

def init_firebase(app):
    """
    Init firebase Admin and it registered cleaning function.
    """
    app.teardown_appcontext(close_firebase)

def send_notification(token, title, body, data=None):
    """
    Envía una notificación push a un dispositivo específico.
    
    Args:
        token (str): Token FCM del dispositivo destino.
        title (str): Título de la notificación.
        body (str): Cuerpo de la notificación.
        data (dict, opcional): Datos adicionales para la notificación.
    
    Returns:
        str: ID del mensaje enviado o None si hay error.
    """
    if not token:
        logger.error("No se puede enviar notificación: token FCM no proporcionado")
        return None
        
    try:
        # we call get_firebase_app()
        get_firebase_app()
        
        #Se preparan los datos como string como requisitos de FCM
        formatted_data = {}
        if data:
            for key, value in data.items():
                formatted_data[key] = str(value)
        
        # Setting Notification
        message = messaging.Message(
            notification=messaging.Notification(
                title=title,
                body=body
            ),
            data=formatted_data,
            token=token
        )
        
        # Send Notification
        response = messaging.send(message)
        logger.info(f"Notificación enviada correctamente: {response}")
        return response
    except Exception as e:
        logger.error(f"Error al enviar notificación: {str(e)}")
        return None

def send_multicast_notification(tokens, title, body, data=None):
    """
    Envía una notificación push a múltiples dispositivos.
    
    Args:
        tokens (list): Lista de tokens FCM de dispositivos destino.
        title (str): Título de la notificación.
        body (str): Cuerpo de la notificación.
        data (dict, opcional): Datos adicionales para la notificación.
    
    Returns:
        messaging.BatchResponse: Respuesta del envío multicast.
    """
    if not tokens or not isinstance(tokens, list) or len(tokens) == 0:
        logger.error("No se puede enviar notificación multicast: tokens FCM no proporcionados o lista vacía")
        return None
        
    try:
      
        get_firebase_app()
        

        formatted_data = {}
        if data:
            for key, value in data.items():
                formatted_data[key] = str(value)
        
        # Configuraramos la notificación multicast
        message = messaging.MulticastMessage(
            notification=messaging.Notification(
                title=title,
                body=body
            ),
            data=formatted_data,
            tokens=tokens
        )
        
        # Enviar notificaciones multicast
        response = messaging.send_multicast(message)
        logger.info(f"Notificación multicast enviada: {response.success_count} exitosas, {response.failure_count} fallidas")
        
        # Registrar errores de envío si los hay
        if response.failure_count > 0:
            error_responses = [resp for resp in response.responses if not resp.success]
            for i, err_resp in enumerate(error_responses):
                logger.warning(f"Error al enviar notificación {i+1}: {err_resp.exception}")
        
        return response
    except Exception as e:
        logger.error(f"Error al enviar notificación multicast: {str(e)}")
        return None