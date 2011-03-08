from app import app
from cherrypy import wsgiserver

if __name__ == '__main__':
    d = wsgiserver.WSGIPathInfoDispatcher({'/': app})
    server = wsgiserver.CherryPyWSGIServer(('0.0.0.0', 8080), d)
    print "Serving HTTP on port 8080"
    try:
        server.start()
    except KeyboardInterrupt:
        server.stop()
