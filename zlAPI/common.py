from hashlib import sha256
from rich import print as pprint
from datetime import datetime


# zlLogger
class zlLogger:
    """ Wrapper for custom logging """
    @staticmethod
    def print(message, moduleName="DevLogging"):
        """ Default Custom Print """
        pprint(message)

    @staticmethod
    def debug(message, moduleName="DevLogging"):
        """ Custom log for debug """
        pprint(
            f"[bold white]\[zlorg] [Beta - v0.0.0.1] -[/bold white] [bold blue]{datetime.now().strftime('%d/%m/%Y, %H:%M:%S')}[/bold blue]   [light grey]<==>[/light grey]  [bold white]DEBUG[/bold white] [bold blue][{moduleName}][/bold blue] {message}")

    @staticmethod
    def log(message, moduleName="DevLogging"):
        """ Custom log for info """
        pprint(
            f"[bold green]\[zlorg] [Beta - v0.0.0.1] -[/bold green] [bold blue]{datetime.now().strftime('%d/%m/%Y, %H:%M:%S')}[/bold blue]   [light grey]<==>[/light grey]  [bold green]LOG[/bold green] [bold blue][{moduleName}][/bold blue] [bold green]{message}[/bold green]")

    @staticmethod
    def warn(message, moduleName="DevLogging"):
        """ Custom log for warning """
        pprint(
            f"[bold yellow]\[zlorg] [Beta - v0.0.0.1] -[/bold yellow] [bold yellow]{datetime.now().strftime('%d/%m/%Y, %H:%M:%S')}[/bold yellow]   [light grey]<==>[/light grey]  [bold yellow]WARN[/bold yellow] [bold yellow][{moduleName}][/bold yellow] [bold yellow]{message}[/bold yellow]")

    @staticmethod
    def error(message, moduleName="DevLogging"):
        """ Custom log for error """
        pprint(
            f"[bold red]\[zlorg] [Beta - v0.0.0.1] -[/bold red] [bold white]{datetime.now().strftime('%d/%m/%Y, %H:%M:%S')}[/bold white]   [light grey]<==>[/light grey]  [bold red]ERROR[/bold red] [bold white][{moduleName}][/bold white] [bold red]{message}[/bold red]")


# Decorators ⏬⏬⏬

# ---------> Module
def Module(moduleObject):
    def wrapper(classModule):
        classModule.controllers = moduleObject['controllers']
        return classModule
    return wrapper


# ---------> Controller
def Controller(endpoint=''):
    if (not endpoint.startswith('/')):
        endpoint = '/' + endpoint

    def ControllerControllerWrapper(classController, endpoint=endpoint):
        allEndpointsMethods = [method for method in dir(classController) if (not method.startswith(
            '__') and not method.endswith('__'))]
        if (len(allEndpointsMethods) > 0) and endpoint.endswith('/'):
            endpoint = endpoint[:-1]
        allMappingEndpointsMethods = [
            getattr(classController, mapping) for mapping in allEndpointsMethods]
        allMappingEndpointsMethods = [{"requestMethod": mappingData["method"], "uri": endpoint + mappingData["uri"], "function":mappingData["function"], 'hash': sha256((mappingData["method"] + endpoint + mappingData["uri"]).encode('utf-8')).hexdigest()}
                                      for mappingData in allMappingEndpointsMethods]
        return {"name": classController.__name__, "endpoint": endpoint, "routes": allMappingEndpointsMethods}

    return ControllerControllerWrapper


# ---------> GET
def Get(uri=""):
    if (uri != "" and not uri.startswith('/')):
        uri = '/' + uri

    def methodWrapper(function):
        return {"method": "GET", "uri": uri, "function": function}
    return methodWrapper
