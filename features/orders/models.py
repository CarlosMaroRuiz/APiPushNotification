from bson import ObjectId
from datetime import datetime

class Order:
    """
    Modelo para representar un pedido en la aplicación.
    
    Attributes:
        user_id (ObjectId): ID del usuario que realizó el pedido.
        notes (str): Descripción o notas del pedido.
        address (str): Dirección de entrega del pedido.
        user_info (dict): Información del usuario (nombre, teléfono, email).
        status (str): Estado actual del pedido (pending, processing, completed).
        courier_id (ObjectId): ID del repartidor asignado (si existe).
        courier_info (dict): Información del repartidor asignado.
        created_at (datetime): Fecha y hora de creación del pedido.
        updated_at (datetime): Fecha y hora de la última actualización.
        assigned_at (datetime): Fecha y hora de asignación a un repartidor.
        completed_at (datetime): Fecha y hora de finalización del pedido.
    """
    # Constantes para los estados del pedido
    STATUS_PENDING = "pending"
    STATUS_PROCESSING = "processing"
    STATUS_COMPLETED = "completed"
    
    def __init__(self, user_id, notes, address, user_info=None):
        """
        Inicializa un nuevo pedido.
        
        Args:
            user_id (ObjectId): ID del usuario que realiza el pedido.
            notes (str): Descripción o notas del pedido.
            address (str): Dirección de entrega del pedido.
            user_info (dict, optional): Información del usuario (nombre, teléfono, email).
        """
        self.user_id = user_id
        self.notes = notes
        self.address = address
        self.user_info = user_info or {}
        self.status = self.STATUS_PENDING  # Estado inicial: pendiente
        self.courier_id = None  # ID del repartidor (se asigna cuando un repartidor toma el pedido)
        self.courier_info = {}  # Información del repartidor
        self.created_at = datetime.utcnow()
        self.updated_at = self.created_at
        self.assigned_at = None  # Cuando el pedido es tomado por un repartidor
        self.completed_at = None  # Cuando el pedido es completado
    
    def to_dict(self):
        """
        Convierte el objeto a un diccionario para almacenamiento en MongoDB.
        
        Returns:
            dict: Representación del pedido como diccionario.
        """
        return {
            "user_id": self.user_id,
            "notes": self.notes,
            "address": self.address,
            "user_info": self.user_info,
            "status": self.status,
            "courier_id": self.courier_id,
            "courier_info": self.courier_info,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "assigned_at": self.assigned_at,
            "completed_at": self.completed_at
        }
    
    @classmethod
    def from_dict(cls, data):
        """
        Crea una instancia de Order a partir de un diccionario.
        
        Args:
            data (dict): Diccionario con datos del pedido.
            
        Returns:
            Order: Nueva instancia de Order.
        """
        if not data:
            return None
        
        order = cls(
            user_id=data.get("user_id"),
            notes=data.get("notes"),
            address=data.get("address"),
            user_info=data.get("user_info", {})
        )
        order.status = data.get("status", cls.STATUS_PENDING)
        order.courier_id = data.get("courier_id")
        order.courier_info = data.get("courier_info", {})
        order.created_at = data.get("created_at", datetime.utcnow())
        order.updated_at = data.get("updated_at", datetime.utcnow())
        order.assigned_at = data.get("assigned_at")
        order.completed_at = data.get("completed_at")
        return order
    
    @staticmethod
    def serialize_for_api(order_data):
        """
        Serializa los datos del pedido para enviar al cliente.
        
        Args:
            order_data (dict): Datos del pedido desde MongoDB.
            
        Returns:
            dict: Datos del pedido serializados para la API.
        """
        if not order_data:
            return None
            
        # Crear una copia para no modificar el original
        serialized = order_data.copy()
        
        # Convertir ObjectId a string
        if '_id' in serialized:
            serialized['_id'] = str(serialized['_id'])
        if 'user_id' in serialized and isinstance(serialized['user_id'], ObjectId):
            serialized['user_id'] = str(serialized['user_id'])
        if 'courier_id' in serialized and isinstance(serialized['courier_id'], ObjectId):
            serialized['courier_id'] = str(serialized['courier_id'])
        
        # Formatear fechas
        date_fields = ['created_at', 'updated_at', 'assigned_at', 'completed_at']
        for field in date_fields:
            if field in serialized and isinstance(serialized[field], datetime):
                serialized[field] = serialized[field].isoformat()
        
        return serialized
    
    def assign_to_courier(self, courier_id, courier_info):
        """
        Asigna el pedido a un repartidor.
        
        Args:
            courier_id (ObjectId): ID del repartidor.
            courier_info (dict): Información del repartidor.
            
        Returns:
            bool: True si se asignó correctamente.
        """
        if self.status != self.STATUS_PENDING:
            return False
            
        self.courier_id = courier_id
        self.courier_info = courier_info
        self.status = self.STATUS_PROCESSING
        self.assigned_at = datetime.utcnow()
        self.updated_at = self.assigned_at
        return True
    
    def complete(self):
        """
        Marca el pedido como completado.
        
        Returns:
            bool: True si se completó correctamente.
        """
        if self.status != self.STATUS_PROCESSING or not self.courier_id:
            return False
            
        self.status = self.STATUS_COMPLETED
        self.completed_at = datetime.utcnow()
        self.updated_at = self.completed_at
        return True
    
    def is_pending(self):
        """
        Verifica si el pedido está pendiente.
        
        Returns:
            bool: True si el pedido está pendiente.
        """
        return self.status == self.STATUS_PENDING
    
    def is_processing(self):
        """
        Verifica si el pedido está en proceso.
        
        Returns:
            bool: True si el pedido está en proceso.
        """
        return self.status == self.STATUS_PROCESSING
    
    def is_completed(self):
        """
        Verifica si el pedido está completado.
        
        Returns:
            bool: True si el pedido está completado.
        """
        return self.status == self.STATUS_COMPLETED