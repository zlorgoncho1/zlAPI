import socket
from time import perf_counter
import asyncio
from threading import Thread
from .common import zlLogger as zll
from .common import Request
from hashlib import sha256
from .exception import InternalServerErrorException, NotFoundException, BadRequestException
from .__utils import *
from .http import HttpStatus


# zlServer
class zlServer:

    # core
    def __init__(self, HOST, PORT):
        self.HOST, self.PORT = HOST, int(PORT)
        self.server = socket.socket(
            socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_TCP)
        self.server.bind((self.HOST, self.PORT))
        self.MAX_PACKET = 32768
        self.__timeout = 0.000001
        self.standardRoutes = {}
        self.paramsRoutes = {}
        self.requestsHandled = 0
        self.requestsHandledTime = 0

    def start(self, AppModule):
        try:
            zll.log("Starting zlServer ...", "ServerCore")
            self.resolveRoutes(AppModule.controllers)
            zll.log("Server successfully started !", "ServerCore")
            asyncio.run(self.__runserver())
        except KeyboardInterrupt:
            zll.warn("KeyboardInterrupt")
            zll.debug(
                f"Number of requests handled: [{self.requestsHandled}] in [{self.requestsHandledTime}]")
            zll.warn("Server has stopped succesfully !")
            quit()

    async def __runserver(self):
        self.server.listen()
        zll.log(f"Listenning on http://{self.HOST}:{self.PORT}", "ServerCore")
        self.server.settimeout(self.__timeout)
        while True:
            try:
                clientSocket, clientAddr = self.server.accept()
            except TimeoutError:
                continue
            thread = Thread(target=self.handle, args=(
                clientSocket, clientAddr)).start()

    # Routing
    def resolveRoutes(self, controllers):
        for Controller in controllers:
            zll.log(f"{Controller.name} | {Controller.endpoint}",
                    "RoutesResolver")
            self.exploreRoutes(Controller.views)

    def exploreRoutes(self, views):
        for view in views:
            executionTime = perf_counter()
            key = view.key
            if view.hasParams:
                try:
                    self.paramsRoutes[key].append(view)
                except KeyError:
                    self.paramsRoutes[key] = [view]
            else:
                self.standardRoutes[key] = view
            executionTime = (perf_counter() - executionTime)*1000
            zll.plog(f"Mapped {view.method}, {{ {view.endpoint} }}", executionTime,
                     "ViewResolver")

    # Request Traitement

    def handle(self, clientSocket, clientAddr):
        executionTime = perf_counter()
        dataStatus, data = self._recv(clientSocket)
        if (not dataStatus):
            clientSocket.close()
            return None
        try:
            request = self.extractData(data)
            statusCode, statusMessage = self.checkRequestAndExec(
                request, clientSocket)
            executionTime = (perf_counter() - executionTime)*1000
            zll.plog(
                f"{clientAddr} ==> {request.method} - {{ {request.endpoint} }}", executionTime, "RequestHandler", str(statusCode)[0], statusMessage)

        except Exception as error:
            InternalServerErrorException.raise__(
                clientSocket, request.protocol)
            zll.error(error)
            raise error
        finally:
            self.requestsHandled += 1
            self.requestsHandledTime += executionTime
            clientSocket.close()

    def _recv(self, clientSocket):
        clientSocket.settimeout(self.__timeout)
        while True:
            try:
                return True, clientSocket.recv(self.MAX_PACKET)
            except TimeoutError:
                return False, ''

    def checkRequestAndExec(self, request, clientSocket):
        isValid, function = (self.checkEndpoint(request))
        if (not isValid):
            self.response(clientSocket, request.protocol,
                          HttpStatus.BAD_REQUEST.code, HttpStatus.BAD_REQUEST.message)
            return HttpStatus.BAD_REQUEST.code, HttpStatus.BAD_REQUEST.message
        return self.execController(clientSocket, request, function)

    def execController(self, clientSocket, request, function):
        data = function(request)
        statusCode, statusMessage = HttpStatus.OK.code,  HttpStatus.OK.message
        self.response(clientSocket, request.protocol,
                      statusCode, statusMessage, data)
        return statusCode, statusMessage

    # To implement Next
    def checkDataTypeAndSetHeader(self):
        pass

    def extractData(self, data):
        [head, body] = data.decode('utf-8').replace(
            '\r', '').split('\n\n', 1)
        method, endpoint, protocol, headers, queries = self.extractHeadData(
            head)
        standardKey = method + endpoint
        paramsKey = method + str(len(endpoint.split('/')[1:]))
        return Request(method, endpoint, protocol, headers, queries, body, standardKey, paramsKey)

    def extractHeadData(self, head):
        head = head.split('\n')
        method, _endpoint, protocol = head[0].split(' ')
        endpoint = _endpoint.split('?', 1)[0]
        try:
            queries = _endpoint.split('?', 1)[1].split('&')
        except IndexError:
            queries = []
        headers = dict(unFormattedHeader.split(': ', 1)
                       for unFormattedHeader in head[1:])
        return method, endpoint, protocol, headers, queries

    # Response Traitement
    def response(self, clientSocket, protocol, statusCode, statusMessage, content=""):
        responseStatus = formatStatusResponse(
            statusCode, statusMessage, protocol)
        headers = getDefaultHeader(content)
        clientSocket.send(formatHTTPResponse(responseStatus, headers, content))

    # Check
    def checkEndpoint(self, request):
        if (request.standardKey in self.standardRoutes):
            return True, self.standardRoutes[request.standardKey].function
        isValid, function = verifyEndpointDynamicKey(
            self.paramsRoutes, request)
        if isValid:
            return True, function
        return False, None
