b Server
==========

This is the server component used with the Android and iPhone security labs available at https://github.com/SecurityCompass/AndroidLabs and https://github.com/SecurityCompass/iPhoneLabs

Setup
-----

You'll need to install:

* blinker 
* cherrypy
* flask
* flask-sqlalchemy
* simplejson

Run:

    easy_install blinker cherrypy flask flask-sqlalchemy simplejson

Using
-----

To run the HTTP server on port 8080

    python app.py 

To run the HTTPS server on port 8443

    python app.py --ssl --port 8443
