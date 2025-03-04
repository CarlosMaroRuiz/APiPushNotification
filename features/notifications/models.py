from bson import ObjectId
from datetime import datetime

class Notification:
    """
    Modelo para representar una notificación en la aplicación.
    
    Attributes:
        user_id (ObjectId): ID del usuario o repartidor destinatario.
        role (str): Rol del destinatario ('user' o 'courier').
        title (str): Título de la notificación.
        body (str): Contenido/mensaje de la notificación.
        data (dict): Datos adicionales para la notificación (ej. ID de pedido).
        type (str): Tipo de notificación (ej. 'new_order', 'order_assigned', etc).
        related_id (str): ID relacionado (ej. ID de pedido).
        read (bool): Si la notificación ha sido leída.
        created_at (datetime): Fecha y hora de creación de la notificación.
    """
    # Constantes para los tipos de notificaciones
    TYPE_NEW_ORDER = "new_order"
    TYPE_ORDER_ASSIGNED = "order_assigned"
    TYPE_ORDER_COMPLETED = "order_completed"
    TYPE_GENERAL = "general"
    
    # Constantes para los roles
    ROLE_USER = "user"
    ROLE_COURIER = "courier"
    
    def __init__(self, user_id, role, title, body, data=None, notification_type=TYPE_GENERAL, related_id=None):
        """
        Inicializa una nueva notificación.
        
        Args:
            user_id (ObjectId): ID del usuario o repartidor.
            role (str): Rol del destinatario ('user' o 'courier').
            title (str): Título de la notificación.
            body (str): Contenido/mensaje de la notificación.
            data (dict, optional): Datos adicionales para la notificación.
            notification_type (str, optional): Tipo de notificación.
            related_id (str, optional): ID relacionado (ej. ID de pedido).
        """
        self.user_id = user_id
        self.role = role
        self.title = title
        self.body = body
        self.data = data or {}
        self.type = notification_type
        self.related_id = related_id
        self.read = False
        self.created_at = datetime.utcnow()
    
    def to_dict(self):
        """
        Convierte el objeto a un diccionario para almacenamiento en MongoDB.
        
        Returns:
            dict: Representación de la notificación como diccionario.
        """
        return {
            "user_id": self.user_id,
            "role": self.role,
            "title": self.title,
            "body": self.body,
            "data": self.data,
            "type": self.type,
            "related_id": self.related_id,
            "read": self.read,
            "created_at": self.created_at
        }
    
    @classmethod
    def from_dict(cls, data):
        """
        Crea una instancia de Notification a partir de un diccionario.
        
        Args:
            data (dict): Diccionario con datos de la notificación.
            
        Returns:
            Notification: Nueva instancia de Notification.
        """
        if not data:
            return None
        
        notification = cls(
            user_id=data.get("user_id"),
            role=data.get("role"),
            title=data.get("title"),
            body=data.get("body"),
            data=data.get("data", {}),
            notification_type=data.get("type", cls.TYPE_GENERAL),
            related_id=data.get("related_id")
        )
        notification.read = data.get("read", False)
        notification.created_at = data.get("created_at", datetime.utcnow())
        return notification
    
    @staticmethod
    def serialize_for_api(notification_data):
        """
        Serializa los datos de la notificación para enviar al cliente.
        
        Args:
            notification_data (dict): Datos de la notificación desde MongoDB.
            
        Returns:
            dict: Datos de la notificación serializados para la API.
        """
        if not notification_data:
            return None
            
        # Crear una copia para no modificar el original
        serialized = notification_data.copy()
        
        # Convertir ObjectId a string
        if '_id' in serialized:
            serialized['_id'] = str(serialized['_id'])
        if 'user_id' in serialized and isinstance(serialized['user_id'], ObjectId):
            serialized['user_id'] = str(serialized['user_id'])
        
        # Formatear fechas
        if 'created_at' in serialized and isinstance(serialized['created_at'], datetime):
            serialized['created_at'] = serialized['created_at'].isoformat()
        
        return serialized
    
    def mark_as_read(self):
        """
        Marca la notificación como leída.
        
        Returns:
            bool: Siempre True, para indicar que se completó la operación.
        """
        self.read = True
        return True
    
    @classmethod
    def get_by_id(cls, db, notification_id, user_id=None, role=None):
        """
        Obtiene una notificación por su ID, opcionalmente verificando el usuario y rol.
        
        Args:
            db: Conexión a la base de datos.
            notification_id (str): ID de la notificación.
            user_id (str, optional): ID del usuario para verificar propiedad.
            role (str, optional): Rol para verificar propiedad.
            
        Returns:
            Notification: Instancia de Notification o None si no se encuentra.
        """
        try:
            query = {"_id": ObjectId(notification_id)}
            
            # Si se proporciona usuario y rol, verificar propiedad
            if user_id and role:
                query["user_id"] = ObjectId(user_id)
                query["role"] = role
                
            notification_data = db.notifications.find_one(query)
            if notification_data:
                return cls.from_dict(notification_data)
            return None
        except Exception:
            return None