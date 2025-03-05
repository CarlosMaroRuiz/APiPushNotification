from flask import jsonify, request
from features.auth.services import register_user,register_courier,login_courier,login_user,update_fcm_token,get_courier_info,get_user_info
import logging
from schemas import validate_schema
from schemas.auth import LoginSchema,RegisterCourierSchema,UpdateFCMTokenSchema,RegisterUserSchema
from core.middleware import token_required

logger = logging.getLogger(__name__)

@validate_schema(RegisterUserSchema)
def register_user_controller(validated_data):
    print("entro")
    """
    Registra un nuevo usuario.
    
    Args:
        validated_data (dict): Datos validados del esquema.
        
    Returns:
        Response: Respuesta JSON con el resultado.
    """
    result = register_user(
        validated_data['email'],
        validated_data['name'],
        validated_data['phone'],
        validated_data['password'],
        validated_data['fcm_token']
    )
    
    if result:
        return jsonify({
            "user": result
        }), 201
    else:
        return jsonify({
            "error": "No se pudo registrar el usuario, verifique que el correo no esté en uso o que el token FCM sea válido"
        }), 400

@validate_schema(RegisterCourierSchema)
def register_courier_controller(validated_data):
    """
    Registra un nuevo repartidor.
    
    Args:
        validated_data (dict): Datos validados del esquema.
        
    Returns:
        Response: Respuesta JSON con el resultado.
    """
    result = register_courier(
        validated_data['email'],
        validated_data['name'],
        validated_data['phone'],
        validated_data['password'],
        validated_data['fcm_token']
    )
    
    if result:
        return jsonify({
            "message": "Repartidor registrado correctamente",
            "courier": result
        }), 201
    else:
        return jsonify({
            "error": "No se pudo registrar el repartidor, verifique que el correo no esté en uso o que el token FCM sea válido"
        }), 400

@validate_schema(LoginSchema)
def login_user_controller(validated_data):
    """
    Inicia sesión de un usuario.
    
    Args:
        validated_data (dict): Datos validados del esquema.
        
    Returns:
        Response: Respuesta JSON con el token y datos del usuario.
    """
    token, user_data = login_user(
        validated_data['email'],
        validated_data['password'],
        validated_data['fcm_token']
    )
    
    if token and user_data:
        return jsonify({
            "access_token": token,
        }), 200
    else:
        return jsonify({
            "error": "Credenciales inválidas o token FCM no válido"
        }), 401

@validate_schema(LoginSchema)
def login_courier_controller(validated_data):
    """
    Inicia sesión de un repartidor.
    
    Args:
        validated_data (dict): Datos validados del esquema.
        
    Returns:
        Response: Respuesta JSON con el token y datos del repartidor.
    """
    token, courier_data = login_courier(
        validated_data['email'],
        validated_data['password'],
        validated_data['fcm_token']
    )
    
    if token and courier_data:
        return jsonify({
            "message": "Inicio de sesión exitoso",
            "token": token,
            "courier": courier_data
        }), 200
    else:
        return jsonify({
            "error": "Credenciales inválidas o token FCM no válido"
        }), 401

@token_required
@validate_schema(UpdateFCMTokenSchema)
def update_fcm_token_controller(validated_data):
    """
    Actualiza el token FCM de un usuario o repartidor.
    
    Args:
        validated_data (dict): Datos validados del esquema.
        
    Returns:
        Response: Respuesta JSON con el resultado.
    """
    from flask import g
    
    result = update_fcm_token(
        g.user_id,
        g.role,
        validated_data['fcm_token']
    )
    
    if result:
        return jsonify({
            "message": "Token FCM actualizado correctamente"
        }), 200
    else:
        return jsonify({
            "error": "No se pudo actualizar el token FCM"
        }), 400

@token_required
def get_profile():
    """
    Obtiene el perfil del usuario o repartidor autenticado.
    
    Returns:
        Response: Respuesta JSON con los datos del perfil.
    """
    from flask import g
    
    if g.role == 'user':
        user_data = get_user_info(str(g.user_id))
        return jsonify({
            "user": user_data
        }), 200
    else:  # courier
        courier_data = get_courier_info(str(g.user_id))
        return jsonify({
            "courier": courier_data
        }), 200