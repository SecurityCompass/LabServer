from app import app
from cherrypy import wsgiserver
if __name__ == '__main__':
    wsgiserver.CherryPyWSGIServer.ssl_certificate = "keys/server.crt"
    wsgiserver.CherryPyWSGIServer.ssl_private_key = "keys/server.key"
    d = wsgiserver.WSGIPathInfoDispatcher({'/': app})
    server = wsgiserver.CherryPyWSGIServer(('0.0.0.0', 8443), d)
    
    print "Serving HTTPS on port 8443"
    try:
        server.start()
    except KeyboardInterrupt:
        server.stop()
        
