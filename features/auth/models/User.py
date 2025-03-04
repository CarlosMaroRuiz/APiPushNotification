from bson import ObjectId
from datetime import datetime

class User:
    """
    Modelo para representar a un usuario de la aplicación.
    
    Attributes:
        email (str): Correo electrónico del usuario (único).
        name (str): Nombre completo del usuario.
        phone (str): Número de teléfono del usuario.
        password_hash (str): Hash de la contraseña (no la contraseña en texto plano).
        fcm_token (str): Token de Firebase Cloud Messaging para notificaciones push.
        created_at (datetime): Fecha y hora de creación del usuario.
        updated_at (datetime): Fecha y hora de la última actualización.
    """
    def __init__(self, email, name, phone, password_hash, fcm_token):
        """
        Inicializa un nuevo usuario.
        
        Args:
            email (str): Correo electrónico del usuario.
            name (str): Nombre completo del usuario.
            phone (str): Número de teléfono del usuario.
            password_hash (str): Hash de la contraseña.
            fcm_token (str): Token FCM para notificaciones push (obligatorio).
        """
        self.email = email
        self.name = name
        self.phone = phone
        self.password_hash = password_hash
        self.fcm_token = fcm_token  # FCM token obligatorio
        self.created_at = datetime.utcnow()
        self.updated_at = self.created_at
        self.last_login = None
        self.active = True  # Por defecto, el usuario está activo
    
    def to_dict(self):
        """
        Convierte el objeto a un diccionario para almacenamiento en MongoDB.
        
        Returns:
            dict: Representación del usuario como diccionario.
        """
        return {
            "email": self.email,
            "name": self.name,
            "phone": self.phone,
            "password_hash": self.password_hash,
            "fcm_token": self.fcm_token,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "last_login": self.last_login,
            "active": self.active
        }
    
    @classmethod
    def from_dict(cls, data):
        """
        Crea una instancia de User a partir de un diccionario.
        
        Args:
            data (dict): Diccionario con datos del usuario.
            
        Returns:
            User: Nueva instancia de User.
        """
        if not data:
            return None
            
        user = cls(
            email=data.get("email"),
            name=data.get("name"),
            phone=data.get("phone"),
            password_hash=data.get("password_hash"),
            fcm_token=data.get("fcm_token")
        )
        
        # Atributos opcionales
        user.created_at = data.get("created_at", datetime.utcnow())
        user.updated_at = data.get("updated_at", datetime.utcnow())
        user.last_login = data.get("last_login")
        user.active = data.get("active", True)
        
        return user
    
    @staticmethod
    def serialize_for_api(user_data):
        """
        Serializa los datos del usuario para enviar al cliente.
        Elimina datos sensibles como la contraseña.
        
        Args:
            user_data (dict): Datos del usuario desde MongoDB.
            
        Returns:
            dict: Datos del usuario serializados y seguros para enviar al cliente.
        """
        if not user_data:
            return None
            
        # Crear una copia para no modificar el original
        serialized = user_data.copy()
        
        # Convertir ObjectId a string
        if '_id' in serialized:
            serialized['_id'] = str(serialized['_id'])
        
        # Eliminar datos sensibles
        serialized.pop('password_hash', None)
        
        # Formatear fechas
        for date_field in ['created_at', 'updated_at', 'last_login']:
            if date_field in serialized and isinstance(serialized[date_field], datetime):
                serialized[date_field] = serialized[date_field].isoformat()
        
        return serialized
    
    def update_fcm_token(self, new_token):
        """
        Actualiza el token FCM del usuario.
        
        Args:
            new_token (str): Nuevo token FCM.
            
        Returns:
            bool: True si se actualizó, False si el token es inválido.
        """
        if not new_token:
            return False
            
        self.fcm_token = new_token
        self.updated_at = datetime.utcnow()
        return True
    
    def record_login(self):
        """
        Registra un inicio de sesión exitoso.
        """
        self.last_login = datetime.utcnow()
        self.updated_at = self.last_login
    
    def deactivate(self):
        """
        Desactiva el usuario.
        """
        self.active = False
        self.updated_at = datetime.utcnow()
    
    def activate(self):
        """
        Activa el usuario.
        """
        self.active = True
        self.updated_at = datetime.utcnow()
    
    def update_profile(self, name=None, phone=None):
        """
        Actualiza el perfil del usuario.
        
        Args:
            name (str, optional): Nuevo nombre.
            phone (str, optional): Nuevo teléfono.
            
        Returns:
            bool: True si se actualizó algún campo.
        """
        updated = False
        
        if name and name != self.name:
            self.name = name
            updated = True
            
        if phone and phone != self.phone:
            self.phone = phone
            updated = True
            
        if updated:
            self.updated_at = datetime.utcnow()
            
        return updated
    
    @classmethod
    def get_by_id(cls, db, user_id):
        """
        Obtiene un usuario por su ID.
        
        Args:
            db: Conexión a la base de datos.
            user_id (str): ID del usuario.
            
        Returns:
            User: Instancia de User o None si no se encuentra.
        """
        try:
            user_data = db.users.find_one({"_id": ObjectId(user_id)})
            if user_data:
                return cls.from_dict(user_data)
            return None
        except Exception:
            return None
    
    @classmethod
    def get_by_email(cls, db, email):
        """
        Obtiene un usuario por su correo electrónico.
        
        Args:
            db: Conexión a la base de datos.
            email (str): Correo electrónico.
            
        Returns:
            User: Instancia de User o None si no se encuentra.
        """
        try:
            user_data = db.users.find_one({"email": email})
            if user_data:
                return cls.from_dict(user_data)
            return None
        except Exception:
            return None