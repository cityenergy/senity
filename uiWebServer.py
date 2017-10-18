import SimpleHTTPServer
import SocketServer
import os
import sys
import logging

# The web handler (mainly created so as to mute the server's log messages)
class webHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):
    def log_message(self, format, *args):
        return

# Senity's web server
class uiWebServer:

    def __init__(self, port, baseDir):
        self.port = port
        self.baseDir = baseDir
        self.senityLogger = logging.getLogger("senity_allInOneSite")

    def start(self):

        handler = webHandler
        try:
            webDir = os.path.join(os.path.dirname(__file__), self.baseDir)
            os.chdir(webDir)

            httpd = SocketServer.TCPServer(("", self.port), handler)
            httpd.serve_forever()
        except Exception:
            print("Senity's internal web server could not be started. Check base directory or port number.")
            self.senityLogger.error("Senity's internal web server could not be started. Check base directory or port number.")
