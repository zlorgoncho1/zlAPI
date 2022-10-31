from .http import HttpStatus
from .__utils import *
from .common import zlLogger as zll


class HttpException:
    def __init__(self, status):
        self.message = status.message
        self.statusCode = status.code

    def raise__(self, clientSocket, protocol):
        status = formatStatusResponse(self.statusCode, self.message,
                                      protocol)
        message = dictToJson(
            {"message": self.message, "statusCode": self.statusCode})
        headers = dictToHTTPHeadersResponse({
            'Content-Type': 'application/json; charset=utf-8',
            'Content-Length': len(message),
            'Connection': 'close',
        })
        clientSocket.send(formatHTTPResponse(status, "", message))


NotFoundException = HttpException(HttpStatus.NOT_FOUND)
InternalServerErrorException = HttpException(HttpStatus.INTERNAL_SERVER_ERROR)
BadRequestException = HttpException(HttpStatus.BAD_REQUEST)
