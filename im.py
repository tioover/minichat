#!/usr/bin/python2
#coding:utf-8
import tornado.ioloop
import tornado.options
import tornado.web
import os.path
import redis
import time
import json

from tornado.options import define, options

define("port", default=8888, type=int)

class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r"/", Main),
            (r"/add/", NewItem),
            (r"/api/items.json", Items),
        ]
        settings = dict(
            #cookie_secret="57oEAzKXQAGaYooo5mEmGeJ*FrQh7EQn_2XdTPmIKU1o/Vo=",
            xsrf_cookies=False,
            template_path=os.path.join(os.path.dirname(__file__), "templates"),
            static_path=os.path.join(os.path.dirname(__file__), "static"),
        )
        tornado.web.Application.__init__(self, handlers, **settings)

class DataBase:
    db = redis.Redis(host='localhost', port=6379, db=0)
    def items(self):
        '''Get items into dict'''
        items = []
        if self.db.get("item:id:max"):
            i = int(self.db.get("item:id:max"))
            now = 1
            while now <= i:
                items.append({
                    'content' : self.db.hget("item:content",now),
                    'name' : self.db.hget("item:name",now),
                    'email' : self.db.hget("item:email",now),
                    'date' : self.db.hget("item:date",now),
                })
                now += 1
        return items

class Base(tornado.web.RequestHandler):
    db = DataBase.db

class Main(Base):
    def get(self):
        self.render("index.html",items=DataBase().items())

class NewItem(Base):
    def get(self):
        message = {
            "id": str(self.db.incr("item:id:max")),
            "name": self.get_argument("name"),
            "email": self.get_argument("email"),
            "content": self.get_argument("content"),
        }
        nowtime = time.strftime('%Y-%m-%d %H:%M',time.localtime(time.time()))
        self.db.hset("item:content",message['id'],message['content'])
        self.db.hset("item:name",message['id'],message['name'])
        self.db.hset("item:email",message['id'],message['email'])
        self.db.hset("item:date",message['id'],nowtime)
        self.redirect("/")

class Items(Base):
    def get(self):
        items = DataBase().items()
        self.write(json.dumps(items))

def main():
    tornado.options.parse_command_line()
    app = Application()
    app.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()


if __name__ == "__main__":
    main()
