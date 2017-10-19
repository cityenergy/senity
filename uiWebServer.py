import SimpleHTTPServer
import SocketServer
import os
import sys
import logging

# HTTPRequest handler (used actually in order to "mute" loggin output
class httpRequestHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):
    def log_message(self, format, *args):
        return

# Senity's web server
class uiWebServer:

    def __init__(self, port, baseDir):
        self.port = port
        self.baseDir = baseDir
        self.senityLogger = logging.getLogger("senity_allInOneSite")

    def start(self):
        try:
            webDir = os.path.join(os.path.dirname(__file__), self.baseDir)
            os.chdir(webDir)

            handler = httpRequestHandler
            self.httpd = SocketServer.TCPServer(("", self.port), handler)
            self.httpd.serve_forever()
        except Exception:
            print("Senity's internal web server could not be started. Check base directory or port number.")
            self.senityLogger.error("Senity's internal web server could not be started. Check base directory or port number.")

