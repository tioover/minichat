#!/usr/bin/python2
#coding:utf-8
import tornado.ioloop
import tornado.options
import tornado.web
import os.path
import redis
import time
import json
import uuid
import subprocess

from tornado.options import define, options

define("port", default=8888, type=int)

class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r"/", Main),
            (r"/add/", AddItem),
            (r"/items.json", Items),
            (r"/post_id.json", PostID),
        ]
        settings = dict(
            xsrf_cookies=False,
            template_path=os.path.join(os.path.dirname(__file__), "templates"),
            static_path=os.path.join(os.path.dirname(__file__), "static"),
        )
        tornado.web.Application.__init__(self, handlers, **settings)


class Base(tornado.web.RequestHandler):
    #This project mainly uses REDIS database, see http://redis.io/ .
    db = redis.Redis(host='localhost', port=6379, db=0)

    def items(self):
        '''Get Allitems into dict.'''
        items = []
        if self.db.get("item:id:max"):
            maxid = int(self.db.get("item:id:max"))
            now = 1
            while now <= maxid:
                items.append({
                    'content' : self.db.hget("item:content",now),
                    'name' : self.db.hget("item:name",now),
                    'email' : self.db.hget("item:email",now),
                    'date' : self.db.hget("item:date",now),
                })
                now += 1
        return items

    def additem(self,item):
        '''As the name suggests.'''
        nowtime = time.strftime('%Y-%m-%d %H:%M',time.localtime(time.time()))
        self.db.hset("item:content",item['id'],item['content'])
        self.db.hset("item:name",item['id'],item['name'])
        self.db.hset("item:email",item['id'],item['email'])
        self.db.hset("item:date",item['id'],nowtime)
        check = self.db.lrem("post_id",item["post_id"],0)
        return check


class Main(Base):
    def get(self):
        self.render("index.html",items=self.items())

class AddItem(Base):
    def post(self):
        item = {
            "id" : str(self.db.incr("item:id:max")),
            "name" : self.get_argument("name"),
            "email" : self.get_argument("email"),
            "content" : self.get_argument("content"),
            "post_id" : self.get_argument("post_id"),
        }
        if self.additem(item):
            self.write(json.dumps("success"))
        else:
            #Database does not POST-ID, may be repeated POST.
            self.write(json.dumps("failure"))


class Items(Base):
    '''Get all item.'''
    def get(self):
        self.write(json.dumps(self.items()))

class PostID(Base):
    '''A unique ID to action to prevent repeat POST.'''
    def get(self):
        post_id = str(uuid.uuid4())
        self.db.lpush("post_id",post_id)
        self.write(json.dumps(post_id))

def main():
    subprocess.Popen("/usr/bin/redis-server",
                     stdout=subprocess.PIPE) #start database.
    tornado.options.parse_command_line()
    app = Application()
    app.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()


if __name__ == "__main__":
    main()
