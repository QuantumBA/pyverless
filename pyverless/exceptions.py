class BadRequest(Exception):

    def __init__(self, message='Bad Request', field=None):
        super(BadRequest, self).__init__(message)
        self.code = 400
        if field:
            self.field = field


class Unauthorized(Exception):

    def __init__(self, message='Unauthorized'):
        super(Unauthorized, self).__init__(message)
        self.code = 401


class Forbidden(Exception):

    def __init__(self, message='Forbidden'):
        super(Forbidden, self).__init__(message)
        self.code = 403


class NotFound(Exception):

    def __init__(self, message='Resource Not Found', field=None):
        super(NotFound, self).__init__(message)
        self.code = 404
        if field:
            self.field = field


class ServerError(Exception):

    def __init__(self, message='Internal Server Error'):
        super(ServerError, self).__init__(message)
        self.code = 500
