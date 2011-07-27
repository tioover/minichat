#!/usr/bin/python2
#coding:utf-8
import tornado.ioloop
import tornado.options
import tornado.web
import os.path
import redis
import time
import json
import subprocess
import hashlib

from tornado.options import define, options

define("port", default=80, type=int)

class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r"/", Index),
            (r"/add/", AddItem),
            (r"/items.json", Items),
            (r"/comet.json", Comet),
        ]
        settings = dict(
            xsrf_cookies=False,
            template_path=os.path.join(os.path.dirname(__file__), "templates"),
            static_path=os.path.join(os.path.dirname(__file__), "static"),
        )
        tornado.web.Application.__init__(self, handlers, **settings)


class DataBase():
    #This project mainly uses REDIS database, see http://redis.io/ .
    db = redis.Redis(host='localhost', port=6379, db=0)

    def items(self):
        '''Get Allitems into dict.'''
        items = []
        if self.db.get("item:id:max"):
            itemid = self.maxid()
            while itemid >= 1:
                items.append({
                    'content' : self.db.hget("item:content",itemid),
                    'name' : self.db.hget("item:name",itemid),
                    'avatar' :  self.avatar_link(self.db.hget("item:email",itemid)),
                    'date' : self.db.hget("item:date",itemid),
                    'id' : itemid,
                })
                itemid -= 1
        return items

    def additem(self,item):
        '''As the name suggests.'''
        nowtime = time.strftime('%Y-%m-%d %H:%M',time.localtime(time.time()))
        self.db.hset("item:content",item['id'],item['content'])
        self.db.hset("item:name",item['id'],item['name'])
        self.db.hset("item:email",item['id'],item['email'])
        self.db.hset("item:date",item['id'],nowtime)

    def maxid(self):
        return int(self.db.get("item:id:max"))

    def maxidplus(self):
        return int(self.db.incr("item:id:max"))

    def avatar_link(self,email):
        if email == None: return None
        md5 = hashlib.md5(email)
        md5.digest()
        emailmd5 = md5.hexdigest()
        link = "http://0.gravatar.com/avatar/"+emailmd5+"?s=68&d=monsterid&r=G"
        return link


class Poll():
    waiter = []
    def queue(self,callback,sence):
        me = Poll
        me.waiter.append({
            "callback" : callback,
            "sence" : sence,
        })

    def radiate(self):
        me = Poll
        for waiter in me.waiter:
            newitems_num = int(DataBase().maxid()) - int(waiter["sence"])
            newitems = DataBase().items()[:newitems_num]
            waiter["callback"](newitems)
        Poll.waiter = []


class Comet(tornado.web.RequestHandler):
    @tornado.web.asynchronous
    def get(self):
        sence = self.get_argument("sence")
        Poll().queue(self.send,sence)

    def send(self,newitems):
        try:
            self.finish(json.dumps(newitems))
        except IOError:
            pass


class Index(tornado.web.RequestHandler):
    # If have Nginx, This class is useless.
    def get(self):
        self.render("index.html")

class AddItem(tornado.web.RequestHandler):
    def post(self):
        item = {
            "id" : str(DataBase().maxidplus()),
            "name" : self.get_argument("name"),
            "email" : self.get_argument("email"),
            "content" : self.get_argument("content"),
        }
        DataBase().additem(item)
        Poll().radiate()


class Items(tornado.web.RequestHandler):
    '''Get all item.'''
    def get(self):
        self.write(json.dumps(DataBase().items()))

def main():
    subprocess.Popen("/usr/bin/redis-server",
                     stdout=subprocess.PIPE) #start database.
    tornado.options.parse_command_line()
    app = Application()
    app.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()

if __name__ == "__main__":
    main()
