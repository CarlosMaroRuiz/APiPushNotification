class AppError(Exception):
    """Clase base para excepciones de la aplicación."""
    def __init__(self, message="Error en la aplicación", status_code=500):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)

class AuthError(AppError):
    """Excepción para errores de autenticación."""
    def __init__(self, message="Error de autenticación", status_code=401):
        super().__init__(message, status_code)

class ValidationError(AppError):
    """Excepción para errores de validación."""
    def __init__(self, message="Error de validación", status_code=400, errors=None):
        self.errors = errors or {}
        super().__init__(message, status_code)

class ResourceNotFoundError(AppError):
    """Excepción para recursos no encontrados."""
    def __init__(self, message="Recurso no encontrado", status_code=404):
        super().__init__(message, status_code)

class DatabaseError(AppError):
    """Excepción para errores de base de datos."""
    def __init__(self, message="Error de base de datos", status_code=500):
        super().__init__(message, status_code)

class FirebaseError(AppError):
    """Excepción para errores de Firebase."""
    def __init__(self, message="Error en Firebase", status_code=500):
        super().__init__(message, status_code)

class FCMTokenError(AppError):
    """Excepción para errores relacionados con tokens FCM."""
    def __init__(self, message="Error con token FCM", status_code=400):
        super().__init__(message, status_code)

class ConflictError(AppError):
    """Excepción para conflictos de recursos (ej. correo ya registrado)."""
    def __init__(self, message="Conflicto con recurso existente", status_code=409):
        super().__init__(message, status_code)