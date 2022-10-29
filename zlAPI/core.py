import socket
import asyncio
from threading import Thread
from .common import zlLogger as zll
from hashlib import sha256


# zlServer
class zlServer(socket.socket):

    # core
    def __init__(self, HOST, PORT):
        self.HOST, self.PORT = HOST, int(PORT)
        self.server = socket.socket(
            socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_TCP)
        self.server.bind((self.HOST, self.PORT))
        self.MAX_PACKET = 32768
        self.__timeout = 0.000001
        self.routes = {}

    def start(self, AppModule):
        try:
            zll.log("Starting zlServer ...", "ServerCore")
            self.resolveRoutes(AppModule.controllers)
            zll.log("Server successfully started !", "ServerCore")
            asyncio.run(self.__runserver())
        except KeyboardInterrupt:
            zll.warn("KeyboardInterrupt")
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
            zll.log(f"{Controller['name']} | {{ {Controller['endpoint']} }}",
                    "RoutesResolver")
            self.exploreRoutes(Controller["routes"])

    def exploreRoutes(self, routes):
        for route in routes:
            zll.log(f"Mapped {{ {route['requestMethod']}, {route['uri']} }}",
                    "RoutesExplorer")
            self.routes[f"{route['hash']}"] = route

    # Request Traitement
    def handle(self, clientSocket, clientAddr):
        dataStatus, data = self._recv(clientSocket)
        if (not dataStatus):
            clientSocket.close()
            return None
        try:
            requestObject = self.extractData(data)
            zll.log(
                f"{clientAddr} ==> {requestObject['method']} - {{ {requestObject['uri']} }}", "RequestHandler")
            if (not self.checkEndpoint(requestObject["hash"])):
                self.statusResponse(
                    clientSocket, requestObject["protocol"], 404, "NOT FOUND")
            else:
                func = self.routes[requestObject["hash"]]["function"]
                response = func()
                self.statusResponse(
                    clientSocket, requestObject["protocol"], 200, "OK", response)
        except Exception as error:
            zll.error(error)
            self.statusResponse(
                clientSocket, requestObject["protocol"], 500, "INTERNAL SERVER ERROR")
            raise error
        finally:
            clientSocket.close()

    def _recv(self, clientSocket):
        clientSocket.settimeout(self.__timeout)
        while True:
            try:
                return True, clientSocket.recv(self.MAX_PACKET).decode('utf-8')
            except TimeoutError:
                return False, ''

    def extractData(self, data):
        [requestHead, requestBody] = data.replace(
            '\r', '').split('\n\n', 1)
        requestMethod, requestUri, requestProtocol, requestHeader = self.extractHeadData(
            requestHead)
        requestHash = sha256(
            (requestMethod + requestUri).encode('utf-8')).hexdigest()
        return {"hash": requestHash, "method": requestMethod, "uri": requestUri, "protocol": requestProtocol, "header": requestHeader, "body": requestBody}

    def extractHeadData(self, requestHead):
        requestMethod, requestUri, requestProtocol = requestHead.split('\n')[
            0].split(' ')
        requestHeader = dict(unFormattedHeader.split(': ', 1)
                             for unFormattedHeader in requestHead.split('\n')[1:])
        return requestMethod, requestUri, requestProtocol, requestHeader

    # Response Traitement
    def statusResponse(self, clientSocket, protocol, code, status, message=None):
        responseStatus = f'{protocol} {code} {status}\n\n'
        if message is not None:
            responseStatus = f'{protocol} {code} {status}\n\n' + message
        clientSocket.send(bytes(responseStatus, 'utf-8'))

    # Check

    def checkEndpoint(self, hash):
        try:
            route = self.routes[hash]
            if (bool(route)):
                return True
        except KeyError:
            return False
