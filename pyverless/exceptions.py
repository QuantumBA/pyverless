class BadRequest(Exception):

    def __init__(self, message='Bad Request'):
        super(BadRequest, self).__init__(message)
        self.code = 400


class Unauthorized(Exception):

    def __init__(self, message='Unauthorized'):
        super(Unauthorized, self).__init__(message)
        self.code = 401


class Forbidden(Exception):

    def __init__(self, message='Forbidden'):
        super(Forbidden, self).__init__(message)
        self.code = 403


class NotFound(Exception):

    def __init__(self, message='Resource Not Found'):
        super(BadRequest, self).__init__(message)
        self.code = 404
