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

class Base(tornado.web.RequestHandler):
    '''数据库操作，具体细节可以不用去管'''
    #This project uses REDIS database, see http://redis.io/ .
    db = redis.Redis(host='localhost', port=8842, db=0)

    def items(self):
        '''从数据库获取所有条目'''
        items = []
        if self.maxid():
            itemid = self.maxid()
            while itemid >= 1:
                new_item = {
                    'content': self.db.hget("item:content", itemid),
                    'name': self.db.hget("item:name", itemid),
                    'avatar': self.db.hget("item:avatar", itemid),
                    'date': self.db.hget("item:date", itemid),
                    'id': itemid,
                }
                items.append(new_item)
                itemid -= 1
        return items

    def add_item(self, item):
        '''添加一个新的条目'''
        item["id"] = int(self.db.incr("item:id:max"))
        item['content'] = lib.escape(item['content'])
        nowtime = time.strftime('%Y-%m-%d %H:%M',time.localtime(time.time()))
        self.db.hset("item:content", item['id'], item['content'])
        self.db.hset("item:name", item['id'], item['name'])
        self.db.hset("item:avatar", item['id'], item['avatar'])
        self.db.hset("item:date", item['id'], nowtime)

    def maxid(self):
        try:
            return int(self.db.get("item:id:max"))
        except TypeError:
            return None


class Poll(Base):
    waiter = []
    def queue(self, callback, sence):
        '''排队，将回调函数添加到waiter队列里面'''
        me = Poll
        me.waiter.append({"callback": callback, "sence": sence})

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
        sence = int(self.get_argument("sence", 0))
        #一般情况下如果参数是0的话就立刻返回所有的项目，但是在数据库没有item
        #的情况下服务器会阻塞请求，直到有item.
        if (sence is not 0) or (not self.maxid):
            self.queue(self.send, sence) #添加到等待队列中
        else:
            self.finish(json.dumps(self.items()))

    def send(self,newitems):
        '''作为广播队列中的回调函数，一旦有新条目回调函数就会被调用，
        返回新条目的json。'''
        try:
            self.finish(json.dumps(newitems))
        except IOError:
            print "Happen a IOError"


class AddItem(Poll):
    def post(self):
        '''获取用户提交的条目'''
        if not self.validate(): raise tornado.web.HTTPError(500)
        item = {}
        item['name'] = self.get_argument("name")
        item['avatar'] = lib.gravatar(self.get_argument("email"))
        item['content'] = self.get_argument("content")
        self.add_item(item) #往数据库添加新的条目
        self.broadcast() #给所有进行长轮询的客户端广播新的条目

    def validate(self):
        '''检查输入'''
        if not "name" in self.request.arguments: return False
        elif not "email" in self.request.arguments: return False
        elif not "content" in self.request.arguments: return False
        return True



class Home(Base):
    def get(self):
        self.render("home.html")


handlers = [
    (r"/", Home),
    (r"/add/", AddItem),
    (r"/items.json", GetItems),
]
settings = dict(
    xsrf_cookies = False,
    static_path = 'static',
    debug = True,
    port = 8888,
    template_path = 'templates'
)

def run():
    #创建一个子进程来运行数据库服务器
    subprocess.Popen(
        ("/usr/bin/redis-server", 'redis.conf'), stdout=subprocess.PIPE) 
    tornado.options.parse_command_line()
    app = tornado.web.Application(handlers, **settings)
    app.listen(settings['port'])
    tornado.ioloop.IOLoop.instance().start()


if __name__ == "__main__": run()
