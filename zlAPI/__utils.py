from hashlib import sha256
from pprint import pprint


def dictToJson(__dict):
    return '{' + "".join(f'"{k}":"{v}",' for k,
                         v in __dict.items())[:-1] + '}'


def formatStatusResponse(statusCode, message, protocol="HTTP/1.1"):
    return f"{protocol} {statusCode} {message}"


def dictToHTTPHeadersResponse(headers):
    return ''.join('%s: %s\n' % (k, v) for k, v in
                   headers.items())


def getDefaultHeader(content):
    return dictToHTTPHeadersResponse({
        'Content-Type': 'text/html; charset=utf-8',
        'Content-Length': len(content),
        'Connection': 'close',
    })


def formatHTTPResponse(status, headers="", content=""):
    r = status + '\n'
    r = r + headers if headers != "" else getDefaultHeader(content)
    r = r + '\n' + content
    return bytes(r, 'utf-8')


def verifyEndpointDynamicKey(routes, request):
    try:
        endpoints = request.endpoint.split("/")[1:]
        key = request.paramsKey
        views = routes[key]
        for view in views:
            endpointArray = view.endpointArray.copy()
            requestEndpointArray = endpoints.copy()
            for index, name in view.params:
                request.params[name] = endpoints[int(index)]
                endpointArray.pop(int(index))
                requestEndpointArray.pop(int(index))
            if endpointArray == requestEndpointArray:
                del request.paramsKey
                del request.standardKey
                return True, view.function
        return False, None
    except KeyError:
        return False, None
