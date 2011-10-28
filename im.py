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
import lib

from tornado.options import define, options

define("port", default=8888, type=int)

class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r"/", Home),
            (r"/add/", AddItem),
            (r"/items.json", GetItems),
        ]

        settings = {
            "xsrf_cookies": False,
            "static_path": os.path.join(os.path.dirname(__file__), "static"),
            "debug": True,
        }

        template_path = os.path.join(os.path.dirname(__file__), "templates")
        settings['template_path'] = template_path
        tornado.web.Application.__init__(self, handlers, **settings)


class Database(object):
    '''数据库操作，具体细节可以不用去管'''
    #This project uses REDIS database, see http://redis.io/ .
    db = redis.Redis(host='localhost', port=6379, db=0)

    def items(self):
        '''从数据库获取所有条目'''
        items = []
        if self.db.get("item:id:max"):
            itemid = self.maxid()
            while itemid >= 1:
                items.append({
                    'content': self.db.hget("item:content",itemid),
                    'name': self.db.hget("item:name",itemid),
                    'avatar': lib.gravatar(self.db.hget("item:email",itemid)),
                    'date': self.db.hget("item:date",itemid),
                    'id': itemid,
                })
                itemid -= 1
        return items

    def add_item(self,item):
        '''添加一个新的条目'''
        item["id"] = int(self.db.incr("item:id:max"))
        item['content'] = lib.markdown_to_html(lib.escape(item['content']))
        nowtime = time.strftime('%Y-%m-%d %H:%M',time.localtime(time.time()))
        self.db.hset("item:content",item['id'],item['content'])
        self.db.hset("item:name",item['id'],item['name'])
        self.db.hset("item:email",item['id'],item['email'])
        self.db.hset("item:date",item['id'],nowtime)

    def maxid(self):
        return int(self.db.get("item:id:max"))


class Base(tornado.web.RequestHandler, Database):
    pass


class Poll(Base):
    waiter = []
    def queue(self,callback,sence):
        '''排队，将回调函数添加到waiter队列里面'''
        me = Poll
        me.waiter.append({
            "callback" : callback,
            "sence" : sence,
        })

    def broadcast(self):
        '''广播，调用队列中的回调函数，返回新增的条目，结束长轮询'''
        me = Poll
        for waiter in me.waiter:
            newitems_num = int(self.maxid()) - int(waiter["sence"])
            newitems = self.items()[:newitems_num]
            waiter["callback"](newitems)
        Poll.waiter = []


class GetItems(Poll):
    @tornado.web.asynchronous # 使用Tornado提供的异步非阻塞特性
    def get(self):
        if self.get_argument("sence", None):
            sence = self.get_argument("sence")
            self.queue(self.send, sence) #添加到等待队列中
        else:
            self.finish(json.dumps(self.items()))

    def send(self,newitems):
        '''作为广播队列中的回调函数，一旦有新条目回调函数就会被调用，
        返回新条目的json。'''
        try:
            self.finish(json.dumps(newitems))
        except IOError:
            pass


class AddItem(Poll):
    def post(self):
        '''获取用户提交的条目'''
        if self.check():
            item = {
                "name" : self.get_argument("name"),
                "email" : self.get_argument("email"),
                "content" : self.get_argument("content"),
            }
            self.add_item(item) #往数据库添加新的条目
            self.broadcast() #给所有进行长轮询的客户端广播新的条目

    def check(self):
        '''检查输入'''
        if not "name" in self.request.arguments:
            return False
        elif not "email" in self.request.arguments:
            return False
        elif not "content" in self.request.arguments:
            return False
        return True



class Home(Base):
    '''主页，仅仅有一个页面而且是静态的，如果不单独实用Tornado作为网页服务器的
    话可以直接用服务器加载这个页面'''
    def get(self):
        self.render("home.html")


def main():
    #创建一个子进程来运行数据库服务器
    subprocess.Popen("/usr/bin/redis-server", stdout=subprocess.PIPE) 
    tornado.options.parse_command_line()
    app = Application()
    app.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()

if __name__ == "__main__":
    main()
