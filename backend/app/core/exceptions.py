class ReglaNegocioError(Exception):
    """Error esperado por una regla del negocio (stock insuficiente, producto inactivo, etc.).

    main.py lo convierte en una respuesta HTTP con el código indicado.
    """

    def __init__(self, mensaje: str, status_code: int = 400):
        super().__init__(mensaje)
        self.mensaje = mensaje
        self.status_code = status_code
