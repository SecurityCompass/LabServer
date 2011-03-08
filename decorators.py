gfrom flask import request
from models import *
from app import error
def validate_session(func):
    s = Session.get_by_key(request.args["session_key"])
    if s == None:
        return lambda : error("invalid session key")
    return func
