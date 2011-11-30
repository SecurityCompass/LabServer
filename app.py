import getopt
import sys
from flask import Flask, request, render_template, request_started
from cherrypy import wsgiserver
from functools import wraps
from models import User, Account, Session
from database import db_session
import simplejson as json
import datetime
app = Flask(__name__)

jsonify = json.dumps

"""
* Error table
| E1 | incorrect username or password |
| E2 | invalid session key            |
| E3 | account does not exist         |
| E4 | balance too low                |
| E5 | forbidden                      |
| E6 | permission denied              |

* Success table
| S1 | transfer complete |
"""

DEFAULT_PORT = 8080

def consolelog(sender):
    print " [*] %s [%s] \"%s %s\"" % (request.remote_addr, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), request.method, request.url)


@app.errorhandler(500)
def internal_server_error(error):
    print " [!]", error
    return "Internal Server Error", 500

def error(text):
    return jsonify({"error" : text})

def success(text):
    return jsonify({"success" : text})

def validate_session(f):
    @wraps(f)
    def decorated_f(*args, **kwargs):
        s = Session.get_by_key(request.args["session_key"])
        if s == None:
            return error("E2")
        return f(s, *args, **kwargs)
    return decorated_f

@app.route('/login', methods=['POST'])
def login():
    u = User.query.filter(User.username == request.form["username"]).first()
    if not u or u.password != request.form["password"]:
        return error("E1")
    
    s = Session.get_by_user(u)
    if s is not None:
        db_session.delete(s)
        db_session.commit()
        
    s = Session(u)
    db_session.add(s)
    db_session.commit()

    return jsonify(s.values)


@app.route('/user', methods = ['GET'])
@validate_session
def user(session):
    return jsonify(session.user.values)
    


@app.route('/accounts')
@validate_session
def account(session):
    return jsonify([a.values for a in session.user.accounts])
            

@app.route('/account/balance')
@validate_session
def balance(session):
    return jsonify({"balance" : session.user.account.balance_formatted})

@app.route('/statement')
@validate_session
def statement(session):
    return render_template('statement.html', accounts=session.user.accounts)

@app.route('/transfer', methods=['POST'])
@validate_session
def transfer(session):
    #set accounts from the request 
    from_account = Account.query.filter(Account.account_number == int(request.form["from_account"])).first()
    to_account = Account.query.filter(Account.account_number == int(request.form["to_account"])).first()
    
    if not from_account or not to_account: #validate that accounts exist
        return error("E3")
    
    #parse sent value and transform into cents
    if request.form["amount"].find('.') != -1:
        (dollars, cents) = request.form["amount"].split('.')
        total_cents = int(dollars)*100 + int(cents)
    else:
        total_cents = int(request.form["amount"]) * 100
    
    #validate that balance is big enough
    if from_account.balance < total_cents:
        return error("E4")
    #transfer money
    to_account.balance += total_cents
    from_account.balance -= total_cents
    db_session.commit()
    return success("S1")

def usage():
    print "Runs the FalseSecure Mobile server"
    print "Arguments: "
    print "  --debug     enable debug mode"
    print "  --port p    serve on port p (default 8080)"
    print "  --ssl       enable SSL"
    print "  --help      print this message"

if __name__ == '__main__':
    port = DEFAULT_PORT
    ssl = False
    opts, args = getopt.getopt(sys.argv[1:], "", ["ssl", "debug", "help", "port="])
    for o, a in opts:
        if o == "--help":
            usage()
            sys.exit(2)
        elif o == "--debug":
            app.debug = True
        elif o == "--ssl":
            ssl = True
            wsgiserver.CherryPyWSGIServer.ssl_certificate = "ssl/certs/server.crt"
            wsgiserver.CherryPyWSGIServer.ssl_private_key = "ssl/private/server.key"
        elif o == "--port":
            port = int(a)

    d = wsgiserver.WSGIPathInfoDispatcher({'/': app})
    server = wsgiserver.CherryPyWSGIServer(('0.0.0.0', port), d, timeout=200)

    request_started.connect(consolelog, app)

    print "Serving %s on port %d %s" % ("HTTP" if not ssl else "HTTPS", port, "(debug enabled)" if app.debug else "")
    
    try:
        server.start()
    except KeyboardInterrupt:
        server.stop()

