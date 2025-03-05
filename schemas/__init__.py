from flask import request, jsonify
from functools import wraps
from marshmallow import ValidationError

def validate_schema(schema_class):
    """
    Decorador para validar datos de entrada usando esquemas Marshmallow.
    
    Args:
        schema_class: La clase de esquema Marshmallow a utilizar.
    
    Returns:
        Decorador para validar los datos de entrada de la vista.
    """
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            # Crear instancia del esquema
            schema = schema_class()
            # Obtener datos de la petición según el método
            if request.method == 'GET':
                data = request.args.to_dict()
            else:
                # Para POST, PUT, PATCH, etc.
                if request.is_json:
                    data = request.get_json()
                else:
                    data = request.form.to_dict()
            
            try:
                # Validar datos
                validated_data = schema.load(data)
                
                # Añadir los datos validados a los argumentos
                kwargs['validated_data'] = validated_data
                
                return f(*args, **kwargs)
            
            except ValidationError as err:
                print(err)
                # Devolver errores de validación
                return jsonify({
                    "error": "Error de validación",
                    "details": err.messages
                }), 400
        
        return wrapper
    
    return decorator