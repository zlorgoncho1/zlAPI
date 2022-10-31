from hashlib import sha256
from rich import print as pprint
from datetime import datetime
from .http import HttpMethod
from typing import TypedDict


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
    def log(message, moduleName="DevLogging",):
        """ Custom log for info """
        pprint(
            f"[bold green]\[zlorg] [Beta - v0.0.0.1] -[/bold green] [bold blue]{datetime.now().strftime('%d/%m/%Y, %H:%M:%S')}[/bold blue]   [light grey]<==>[/light grey]  [bold green]LOG[/bold green] [bold blue][{moduleName}][/bold blue] [bold green]{message}[/bold green]")

    @staticmethod
    def plog(message, time="", moduleName="DevLogging", statusCode="0", statusMessage="OK"):
        """ Custom log for request handling """
        if statusCode == "0":
            pprint(
                f"[bold green]\[zlorg] [Beta - v0.0.0.1] -[/bold green] [bold blue]{datetime.now().strftime('%d/%m/%Y, %H:%M:%S')}[/bold blue]   [light grey]<==>[/light grey]  [bold green]LOG[/bold green] [bold blue][{moduleName}][/bold blue] [bold green]{message}[/bold green] [bold yellow]+ {time:.3f} ms[/bold yellow]")
        elif statusCode == "2":
            pprint(
                f"[bold white]\[zlorg] [Beta - v0.0.0.1] - {datetime.now().strftime('%d/%m/%Y, %H:%M:%S')}[/bold white]   [light grey]<==>[/light grey]  [bold green]LOG [{moduleName}] [\"{statusMessage}\"] {message}[/bold green] [bold yellow]+ {time:.3f} ms[/bold yellow]")
        elif statusCode == "3":
            pprint(
                f"[bold white]\[zlorg] [Beta - v0.0.0.1] - {datetime.now().strftime('%d/%m/%Y, %H:%M:%S')}[/bold white]   [light grey]<==>[/light grey]  [bold blue]LOG [{moduleName}] [\"{statusMessage}\"] {message}[/bold blue] [bold yellow]+ {time:.3f} ms[/bold yellow]")
        else:
            pprint(
                f"[bold white]\[zlorg] [Beta - v0.0.0.1] - {datetime.now().strftime('%d/%m/%Y, %H:%M:%S')}[/bold white]   [light grey]<==>[/light grey]  [bold red]LOG [{moduleName}] [\"{statusMessage}\"] {message}[/bold red] [bold yellow]+ {time:.3f} ms[/bold yellow]")

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


# Route
class View__:
    def __init__(self, method, endpoint, function):
        self.method = method
        self.endpoint = endpoint
        self.function = function
        self.key = None
        self.params = []
        self.endpointArray = []
        self.hasParams = False

    def generateKey(self):
        self.endpointArray = self.endpoint.split('/')[1:]
        self.params = [(index, elt.replace(':', ''))
                       for index, elt in enumerate(self.endpointArray) if elt.startswith(':')]
        self.params.reverse()
        if len(self.params) == 0:
            self.hasParams = False
            self.key = self.method + self.endpoint
        else:
            self.hasParams = True
            self.key = self.method + str(len(self.endpointArray))


# Controller__
class Controller__:
    def __init__(self, name, endpoint, views):
        self.name = name
        self.endpoint = endpoint
        self.views = views


# Request
class Request:
    def __init__(self, method, endpoint, protocol, headers, queries, body, standardKey, paramsKey):
        self.method = method
        self.endpoint = endpoint
        self.protocol = protocol
        self.headers = headers
        self.queries = queries
        self.body = body
        self.standardKey = standardKey
        self.paramsKey = paramsKey
        self.params = {}


# Decorators ⏬⏬⏬
# ---------> Controller
def Controller(endpoint: str = ''):
    endpoint = '/' + endpoint if (not endpoint.startswith('/')) else endpoint

    def ControllerControllerWrapper(classController):
        views = [method for method in dir(classController) if (not method.startswith(
            '__') and not method.endswith('__'))]
        uri = endpoint[:-1] if (len(views)
                                > 0) and endpoint.endswith('/') else endpoint

        viewsMapping = [
            getattr(classController, mapping) for mapping in views]
        for viewMapping in viewsMapping:
            viewMapping.endpoint = uri + viewMapping.endpoint
            viewMapping.generateKey()

        # sha256((mappingData["method"] + endpoint + mappingData["uri"]).encode('utf-8')).hexdigest()
        return Controller__(classController.__name__, endpoint, viewsMapping)

    return ControllerControllerWrapper


# ---------> View
def View(method, endpoint=""):
    def viewWrapper(func):
        uri = '/' + \
            endpoint if (
                endpoint != "" and not endpoint.startswith('/')) else endpoint
        return View__(method, uri, func)
    return viewWrapper
