from bson import ObjectId
from datetime import datetime

class Courier:
    """
    Modelo para representar a un repartidor en la aplicación.
    
    Attributes:
        email (str): Correo electrónico del repartidor (único).
        name (str): Nombre completo del repartidor.
        phone (str): Número de teléfono del repartidor.
        password_hash (str): Hash de la contraseña (no la contraseña en texto plano).
        fcm_token (str): Token de Firebase Cloud Messaging para notificaciones push.
        available (bool): Indica si el repartidor está disponible para tomar pedidos.
        created_at (datetime): Fecha y hora de creación del repartidor.
        updated_at (datetime): Fecha y hora de la última actualización.
    """
    def __init__(self, email, name, phone, password_hash, fcm_token):
        """
        Inicializa un nuevo repartidor.
        
        Args:
            email (str): Correo electrónico del repartidor.
            name (str): Nombre completo del repartidor.
            phone (str): Número de teléfono del repartidor.
            password_hash (str): Hash de la contraseña.
            fcm_token (str): Token FCM para notificaciones push (obligatorio).
        """
        self.email = email
        self.name = name
        self.phone = phone
        self.password_hash = password_hash
        self.fcm_token = fcm_token  # FCM token obligatorio
        self.available = True  # Por defecto, el repartidor esta disponible
        self.created_at = datetime.utcnow()
        self.updated_at = self.created_at
        self.last_login = None
        self.active = True  # Por defecto, el repartidor está activo
        self.current_orders_count = 0  # Contador de pedidos activos
        self.total_orders_completed = 0  # Total de pedidos completados
    
    def to_dict(self):
        """
        Convierte el objeto a un diccionario para almacenamiento en MongoDB.
        
        Returns:
            dict: Representación del repartidor como diccionario.
        """
        return {
            "email": self.email,
            "name": self.name,
            "phone": self.phone,
            "password_hash": self.password_hash,
            "fcm_token": self.fcm_token,
            "available": self.available,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "last_login": self.last_login,
            "active": self.active,
            "current_orders_count": self.current_orders_count,
            "total_orders_completed": self.total_orders_completed
        }
    
    @classmethod
    def from_dict(cls, data):
        """
        Crea una instancia de Courier a partir de un diccionario.
        
        Args:
            data (dict): Diccionario con datos del repartidor.
            
        Returns:
            Courier: Nueva instancia de Courier.
        """
        if not data:
            return None
            
        courier = cls(
            email=data.get("email"),
            name=data.get("name"),
            phone=data.get("phone"),
            password_hash=data.get("password_hash"),
            fcm_token=data.get("fcm_token")
        )
        
        # Atributos opcionales
        courier.available = data.get("available", True)
        courier.created_at = data.get("created_at", datetime.utcnow())
        courier.updated_at = data.get("updated_at", datetime.utcnow())
        courier.last_login = data.get("last_login")
        courier.active = data.get("active", True)
        courier.current_orders_count = data.get("current_orders_count", 0)
        courier.total_orders_completed = data.get("total_orders_completed", 0)
        
        return courier
    
    @staticmethod
    def serialize_for_api(courier_data):
        """
        Serializa los datos del repartidor para enviar al cliente.
        Elimina datos sensibles como la contraseña.
        
        Args:
            courier_data (dict): Datos del repartidor desde MongoDB.
            
        Returns:
            dict: Datos del repartidor serializados y seguros para enviar al cliente.
        """
        if not courier_data:
            return None
            
        # Crear una copia para no modificar el original
        serialized = courier_data.copy()
        
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
        Actualiza el token FCM del repartidor.
        
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
    
    def set_availability(self, available):
        """
        Actualiza la disponibilidad del repartidor.
        
        Args:
            available (bool): Estado de disponibilidad.
            
        Returns:
            bool: True siempre, para indicar que el cambio se realizó.
        """
        self.available = bool(available)
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
        Desactiva el repartidor.
        """
        self.active = False
        self.available = False
        self.updated_at = datetime.utcnow()
    
    def activate(self):
        """
        Activa el repartidor.
        """
        self.active = True
        self.updated_at = datetime.utcnow()
    
    def update_profile(self, name=None, phone=None):
        """
        Actualiza el perfil del repartidor.
        
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
    
    def assign_order(self):
        """
        Incrementa el contador de pedidos activos cuando se asigna un nuevo pedido.
        """
        self.current_orders_count += 1
        if self.current_orders_count > 0:
            self.available = False  # Si tiene pedidos activos, ya no está disponible
        self.updated_at = datetime.utcnow()
    
    def complete_order(self):
        """
        Actualiza contadores cuando se completa un pedido.
        
        Returns:
            bool: True si se actualizó correctamente, False si no había pedidos activos.
        """
        if self.current_orders_count <= 0:
            return False
            
        self.current_orders_count -= 1
        self.total_orders_completed += 1
        
        # Si ya no tiene pedidos activos, está disponible de nuevo
        if self.current_orders_count == 0:
            self.available = True
            
        self.updated_at = datetime.utcnow()
        return True
    
    @classmethod
    def get_by_id(cls, db, courier_id):
        """
        Obtiene un repartidor por su ID.
        
        Args:
            db: Conexión a la base de datos.
            courier_id (str): ID del repartidor.
            
        Returns:
            Courier: Instancia de Courier o None si no se encuentra.
        """
        try:
            courier_data = db.couriers.find_one({"_id": ObjectId(courier_id)})
            if courier_data:
                return cls.from_dict(courier_data)
            return None
        except Exception:
            return None
    
    @classmethod
    def get_by_email(cls, db, email):
        """
        Obtiene un repartidor por su correo electrónico.
        
        Args:
            db: Conexión a la base de datos.
            email (str): Correo electrónico.
            
        Returns:
            Courier: Instancia de Courier o None si no se encuentra.
        """
        try:
            courier_data = db.couriers.find_one({"email": email})
            if courier_data:
                return cls.from_dict(courier_data)
            return None
        except Exception:
            return None
    
    @classmethod
    def get_available_couriers(cls, db, limit=None):
        """
        Obtiene los repartidores disponibles.
        
        Args:
            db: Conexión a la base de datos.
            limit (int, optional): Límite de resultados.
            
        Returns:
            list: Lista de instancias de Courier disponibles.
        """
        try:
            query = {"available": True, "active": True}
            cursor = db.couriers.find(query).sort("current_orders_count", 1)
            
            if limit:
                cursor = cursor.limit(limit)
                
            return [cls.from_dict(doc) for doc in cursor]
        except Exception:
            return []