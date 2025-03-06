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
            # Asegurarse de que no haya una aplicación ya inicializada
            try:
                g.firebase_app = firebase_admin.initialize_app(cred)
                logger.info("Firebase Admin SDK inicializado correctamente")
            except ValueError:
                # La aplicación ya está inicializada, obtenemos la aplicación default
                g.firebase_app = firebase_admin.get_app()
                logger.info("Firebase Admin SDK ya estaba inicializado, usando la instancia existente")
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
    
def diagnose_firebase():
    """
    Realiza un diagnóstico simplificado de la configuración de Firebase.
    
    Returns:
        dict: Resultados del diagnóstico
    """
    results = {
        "firebase_initialized": False,
        "connection_test": False,
        "credentials_valid": False,
        "fcm_connectivity": False,
        "firebase_version": None,
        "errors": []
    }
    
    try:
        # Verificar versión de firebase-admin
        try:
            import firebase_admin
            results["firebase_version"] = firebase_admin.__version__
            logger.info(f"Versión de firebase-admin: {firebase_admin.__version__}")
        except Exception as version_error:
            results["errors"].append(f"Error al obtener versión de firebase-admin: {str(version_error)}")
        
        # 1. Verificar inicialización
        try:
            app = firebase_admin.get_app()
            results["firebase_initialized"] = True
            logger.info("Firebase ya está inicializado")
        except ValueError:
            try:
                # Verificar que exista el archivo de credenciales
                cred_path = current_app.config.get('FIREBASE_CREDENTIALS_PATH', 
                            'deliversurimbo-firebase-adminsdk-fbsvc-e7d73aeff9.json')
                
                if not os.path.exists(cred_path):
                    results["errors"].append(f"Archivo de credenciales no encontrado: {cred_path}")
                    return results
                    
                # Intentar cargar las credenciales
                cred = credentials.Certificate(cred_path)
                results["credentials_valid"] = True
                
                # Intenta inicializar Firebase
                app = firebase_admin.initialize_app(cred)
                results["firebase_initialized"] = True
                logger.info("Firebase inicializado durante el diagnóstico")
            except Exception as init_error:
                results["errors"].append(f"Error al inicializar Firebase: {str(init_error)}")
                return results
        
        # 2. Verificar conectividad básica
        import socket
        try:
            socket.create_connection(("www.google.com", 80))
            results["connection_test"] = True
        except OSError as net_error:
            results["errors"].append(f"Problema de conectividad a Internet: {str(net_error)}")
        
        # 3. Intentar enviar un mensaje de prueba a un token inexistente
        try:
            # Token inválido a propósito pero con formato válido
            test_token = "fMvG8xNUR1G3PVX_valid_format_but_invalid_token_aAbBcCdDeEfFgGhH"
            message = messaging.Message(
                notification=messaging.Notification(
                    title="Test",
                    body="Test"
                ),
                token=test_token
            )
            
            try:
                messaging.send(message)
            except messaging.UnregisteredError:
                # Este error es esperado (token inválido) e indica que la conexión a FCM funciona
                results["fcm_connectivity"] = True
                logger.info("Prueba de conectividad FCM exitosa (token inválido)")
            except Exception as send_error:
                error_message = str(send_error)
                if "InvalidArgument" in error_message or "invalid-argument" in error_message:
                    # Este error también es aceptable, pues indica conexión a FCM
                    results["fcm_connectivity"] = True
                    logger.info("Prueba de conectividad FCM exitosa (error de argumento)")
                else:
                    results["errors"].append(f"Error inesperado al probar FCM: {error_message}")
        except Exception as message_error:
            results["errors"].append(f"Error al crear mensaje de prueba: {str(message_error)}")
        
        return results
    except Exception as e:
        results["errors"].append(f"Error general en diagnóstico: {str(e)}")
        return results

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
        messaging.BatchResponse o dict: Respuesta del envío individual o multicast.
    """
    if not tokens or not isinstance(tokens, list) or len(tokens) == 0:
        logger.error("No se puede enviar notificación multicast: tokens FCM no proporcionados o lista vacía")
        return None
        
    # Verificar validez de los tokens FCM (deben ser strings no vacíos)
    valid_tokens = [token for token in tokens if token and isinstance(token, str)]
    
    if len(valid_tokens) == 0:
        logger.error("No hay tokens FCM válidos en la lista")
        return None
    
    if len(valid_tokens) != len(tokens):
        logger.warning(f"Se filtraron {len(tokens) - len(valid_tokens)} tokens inválidos")
        tokens = valid_tokens
    
    try:
        # Si solo tenemos un token, usamos send() en lugar de send_multicast()
        if len(tokens) == 1:
            logger.info("Solo hay un token, enviando notificación individual en lugar de multicast")
            return send_notifications_individually(tokens, title, body, data)
            
        get_firebase_app()
        
        formatted_data = {}
        if data:
            for key, value in data.items():
                formatted_data[key] = str(value)
        
        # Por seguridad, usaremos envío individual para evitar problemas con el endpoint /batch
        logger.info("Enviando notificaciones individualmente para evitar problemas de conexión")
        return send_notifications_individually(tokens, title, body, data)
            
    except Exception as e:
        logger.error(f"Error al enviar notificación multicast: {str(e)}")
        return None

# Versión alternativa: si hay problemas con el endpoint /batch, enviar 
# las notificaciones una por una en lugar de usar multicast
def send_notifications_individually(tokens, title, body, data=None):
    """
    Envía notificaciones individualmente a cada token como alternativa a multicast.
    
    Args:
        tokens (list): Lista de tokens FCM de dispositivos destino.
        title (str): Título de la notificación.
        body (str): Cuerpo de la notificación.
        data (dict, opcional): Datos adicionales para la notificación.
    
    Returns:
        dict: Conteo de éxitos y fallos.
    """
    if not tokens or not isinstance(tokens, list) or len(tokens) == 0:
        logger.error("No se pueden enviar notificaciones: tokens FCM no proporcionados o lista vacía")
        return None
        
    # Filtrar tokens inválidos
    valid_tokens = [token for token in tokens if token and isinstance(token, str)]
    
    if not valid_tokens:
        logger.error("No hay tokens FCM válidos en la lista")
        return None
    
    if len(valid_tokens) != len(tokens):
        logger.warning(f"Se filtraron {len(tokens) - len(valid_tokens)} tokens inválidos")
        tokens = valid_tokens
    
    try:
        get_firebase_app()
        
        formatted_data = {}
        if data:
            for key, value in data.items():
                formatted_data[key] = str(value)
        
        success_count = 0
        failure_count = 0
        responses = []
        
        for i, token in enumerate(tokens):
            try:
                # Verificar formato válido de token FCM (básico)
                if not token or len(token) < 10:
                    logger.warning(f"Token FCM inválido: {token}")
                    failure_count += 1
                    responses.append({'success': False, 'exception': 'Token inválido'})
                    continue
                
                message = messaging.Message(
                    notification=messaging.Notification(
                        title=title,
                        body=body
                    ),
                    data=formatted_data,
                    token=token
                )
                
                # Intentamos enviar con un simple reintento
                try:
                    response = messaging.send(message)
                    success_count += 1
                    responses.append({'success': True})
                    logger.info(f"Notificación enviada correctamente al token {i+1}")
                except Exception as e:
                    # Un reintento simple
                    logger.warning(f"Error al enviar notificación, reintentando: {str(e)}")
                    try:
                        import time
                        time.sleep(1)  # Esperar un segundo antes de reintentar
                        response = messaging.send(message)
                        success_count += 1
                        responses.append({'success': True})
                        logger.info(f"Notificación enviada correctamente al token {i+1} en segundo intento")
                    except Exception as retry_error:
                        failure_count += 1
                        responses.append({'success': False, 'exception': str(retry_error)})
                        logger.warning(f"Error al enviar notificación al token {i+1} después del reintento: {str(retry_error)}")
                
            except Exception as e:
                failure_count += 1
                responses.append({'success': False, 'exception': str(e)})
                logger.warning(f"Error al enviar notificación a token {i+1}: {str(e)}")
        
        # Crear una respuesta de tipo BatchResponse
        class BatchResponse:
            def __init__(self, success_count, failure_count, responses):
                self.success_count = success_count
                self.failure_count = failure_count
                self.responses = responses
        
        result = BatchResponse(success_count, failure_count, responses)
        
        logger.info(f"Notificaciones individuales enviadas: {success_count} exitosas, {failure_count} fallidas")
        return result
        
    except Exception as e:
        logger.error(f"Error general al enviar notificaciones individuales: {str(e)}")
        
        # Verificar conectividad básica
        import socket
        try:
            socket.create_connection(("www.google.com", 80))
            logger.info("La conexión a Internet parece estar funcionando")
        except OSError:
            logger.error("Posible problema de conectividad a Internet")
        
        # Crear una respuesta de error simplificada
        class ErrorResponse:
            def __init__(self):
                self.success_count = 0
                self.failure_count = len(tokens)
                self.responses = []
        
        return ErrorResponse()