from flask import Flask, render_template, request, redirect, abort,jsonify
from flask import make_response

import time
import redis
import uuid

import sys
reload(sys)
sys.setdefaultencoding('utf8')


app = Flask(__name__)

r = None

# class BookItem(object):
#     def __init__(self, title, text):
#         self.title = title
#         self.text = text


@app.route('/')
def index_page():
    index = request.args.get("index")


    user2 = request.args.get("user")

    if user2 is None or len(user2) == 0:
        user = request.cookies.get('user')
        if user is None or len(user) == 0:
            return redirect('/login')

        return redirect('/?user='+user)


    if index is None:
        index = 0

    if index < 0:
        index = 0

    global r
    # r.setex("index",333,10)

    list_name =  "list_uuid"+user2

    n = r.llen(list_name)

    pagesize = 10

    ls_uuid =  r.lrange(list_name, index, pagesize)

    ispagefull = 0
    if(len(ls_uuid) == pagesize):
        ispagefull = 1

    li = []
    for i in range(len(ls_uuid)):
        u = ls_uuid[i];
        title = r.hget(u,"title")
        v = r.hget(u,"text")
        time = r.hget(u,"time")

        li.append({"title":title, "text":v ,"uuid":u , "time":time})

    resp = make_response(render_template('index.html',data=li, pagefull=ispagefull ))

    # resp.set_cookie('index', str(index))

    return  resp

    # return render_template('index.html', data=li)



@app.route('/login')
def login():
    resp = make_response(render_template('login.html'))
    return resp


@app.route('/detail')
def item_detail_page():
    u = request.args.get("uuid")

    t = r.hget(u, "title")
    v = r.hget(u, "text")

    data = {"title": t, "text": v, "uuid": u}

    resp = make_response(render_template('edit.html',cc=data))

    return resp


    # return render_template('edit.html',cc=data)



@app.route('/delte/item',methods=['POST'])
def delete_item():
    global  r
    # u = request.args.get("uuid", "null")
    u = request.form['uuid']

    user = request.cookies.get('user')

    list_name =  "list_uuid"+user


    r.lrem(list_name, u, num=0)

    keys = r.hkeys(u)

    r.hdel(u, keys)

    return jsonify({"code": 200})


@app.route('/edit/update',methods=['POST'])
def update_item():

    global  r
    title = request.form['title']
    text = request.form['text']
    user = request.cookies.get('user')

    if user is None:
        return jsonify({"code": -1,"msg":"please login"})

    struuid = request.form.get('uuid',"")

    isNew = False

    if len(struuid) == 0:
        isNew = True
        struuid = str(uuid.uuid4())


    text2 = text.replace("\n","<br>")




    list_name =  "list_uuid"+user

    t = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

    # r.lpush("list_title",title)
    # r.lpush("list_text",text2)

    if isNew:
        r.lpush(list_name,struuid)


    r.hset(struuid,"title",title)
    r.hset(struuid,"text",text2)
    r.hset(struuid,"time", t)



    return jsonify({"code": 200})


def initRedis():
    global r
    r = redis.Redis(host='127.0.0.1', port=6379)



if __name__ == '__main__':
    initRedis()
    app.run(host="0.0.0.0",debug=True)
