
class HttpStatus__:
    def __init__(self, code, message):
        self.code = code
        self.message = message


class HttpStatus:
    OK = HttpStatus__(200, "OK")
    CREATED = HttpStatus__(201, "Created")
    NO_CONTENT = HttpStatus__(204, "No Content")
    BAD_REQUEST = HttpStatus__(400, "Bad Request")
    UNAUTHORIZED = HttpStatus__(401, "Unauthorized")
    FORBIDDEN = HttpStatus__(403, "Forbidden")
    NOT_FOUND = HttpStatus__(404, "Not Found")
    METHOD_NOT_ALLOWED = HttpStatus__(405, "Method Not Allowed")
    INTERNAL_SERVER_ERROR = HttpStatus__(500, "Internal Server Error")
    NOT_IMPLEMENTED = HttpStatus__(501, "Not Implemented")
    BAD_GATEWAY = HttpStatus__(502, "Bad Gateway")


class HttpMethod:
    GET = "GET"
    POST = "POST"
    PATCH = "PATCH"
    PUT = "PUT"
    DELETE = "DELETE"
    OPTION = "OPTION"


class HttpContentType:
    pass
