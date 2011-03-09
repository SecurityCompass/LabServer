from flask import Flask, request, render_template
from cherrypy import wsgiserver
from functools import wraps
from models import User, Account, Session
from database import db_session
import simplejson as json
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
    return render_template('statement.html', account=session.user.account)

@app.route('/transfer', methods=['POST'])
@validate_session
def transfer(session):
    from_account = session.user.account
    to_account = Account.query.filter(Account.account_number == int(request.form["to_account"])).first()
    if not to_account:
        return error("E3")
    (dollars, cents) = request.form["amount"].split('.')
    total_cents = int(dollars)*100 + int(cents)
    
    if from_account.balance < total_cents:
        return error("E4")

    to_account.balance += total_cents
    from_account.balance -= total_cents
    db_session.commit()
    
    return success("S1")
