import os
import base64

from datetime import datetime
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship, backref
from database import Base, db_session
import settings

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True)
    password = Column(String(50))
    first_name = Column(String(50))
    last_name = Column(String(50))
    
    def __init__(self, username=None, password=None, first_name=None, last_name=None):
        self.username = username
        self.password = password
        self.first_name = first_name
        self.last_name = last_name

    def __repr__(self):
        return '<User %r>' % (self.username)
    
    @property
    def values(self):
        return {"username" : self.username,
                "first_name" : self.first_name,
                "last_name" : self.last_name,
                }

class Account(Base):
    __tablename__ = 'accounts'
    id = Column(Integer, primary_key=True) 
    account_number = Column(Integer, unique=True)
    type = Column(String(50))

    #this is stored in cents!
    balance = Column(Integer)
    
    #users and accounts have a many to one
    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship(User, backref=backref('accounts'))

    def __init__(self, account_number=None, type=type, balance=None, user=None):
        self.account_number = account_number
        self.type = type
        self.balance = balance
        self.user = user

    def __repr__(self):
        return '<Account %r>' % (self.account_number)  

    @property
    def balance_formatted(self):
        return "%d.%02d" % ((self.balance / 100), (self.balance % 100))

    @property
    def values(self):
        return {"account_number" : self.account_number,
                "type" : self.type,
                "balance" : self.balance_formatted,
                }    


class Session(Base):
    __tablename__ = "sessions"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), unique=True)
    user = relationship(User)
    key = Column(String(50), unique=True)
    created = Column(DateTime)
   
    def __init__(self, user=None):
        self.user = user
        self.key = base64.encodestring(os.urandom(24)).strip()
        self.created = datetime.now()

    def __repr__(self):
        return '<Session %r>' % (self.key)
    
    @property
    def values(self):
        return {"username" : self.user.username,
                "key" : self.key,
                "created" : str(self.created),
                }
    @classmethod
    def get_by_key(cls, key):
        s = cls.query.filter(cls.key == key).first()
        #print datetime.now() - s.created
        if s and datetime.now() - s.created > settings.SESSION_LIFETIME:
            s = None
        return s

    @classmethod
    def get_by_user(cls, user):
        s = cls.query.filter(cls.user == user).first()
        if s and datetime.now() - s.created > settings.SESSION_LIFETIME:
            s.query.delete()
            db_session.commit()
            s = None
        return s

    
