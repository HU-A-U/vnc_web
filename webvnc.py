# -*- coding:utf-8 -*-
import sys

reload(sys)
sys.setdefaultencoding("utf8")
import os
import shlex
import random
from flask import g
from flask import request, make_response, Flask
from flask_httpauth import HTTPBasicAuth
from flask_restful import abort
from jinja2 import Environment, FileSystemLoader
from vncdotool import api
import re

STATES = {'state1': {'failed': '1', 'info': 'request question'}}
SCREENT_PNG = r'./{}/screenshot.png'
AUTH_VDO = r'./{}/template.vdo'
env = Environment(loader=FileSystemLoader('./'))
auth = HTTPBasicAuth()
app = Flask(__name__)
app.config['MYSTATIC'] = './user/{}'
app.secret_key = '123456'


class Auths:
    def __init__(self):
        self.client = object

    def ip_filter(self, ip):
        if re.match(r"^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$", ip):
            return True
        else:
            abort(404, message="auth ip doesn't exist")

    def response_filter(self, state):
        if state == 0:
            abort(0, message='unknown error;')
        elif state == 1:
            abort(1, message='parameter error')

    def client_screen(self, path):
        path = path + '/screen.png'
        self.client.captureScreen(path)
        return True

    def port_filter(self, port):
        if port:
            return True
        else:
            abort(404, message="auth port doesn't exist")

    def allocate_vncvdo(self, vdo_path):
        args = [vdo_path]
        while args:
            cmd = args.pop(0)
            if cmd in ('pause', 'sleep'):
                duration = float(args.pop(0)) / 1
                self.client.pause(duration)
            elif cmd in ('kdown', 'keydown'):
                key = args.pop(0)
                self.client.keyDown(key)
            elif cmd in ('kup', 'keyup'):
                key = args.pop(0)
                self.client.keyUp(key)
            elif cmd in ('move', 'mousemove'):
                x, y = int(args.pop(0)), int(args.pop(0))
                self.client.mouseMove(x, y)
            elif cmd == 'click':
                button = int(args.pop(0))
                self.client.mousePress(button)
            elif os.path.isfile(cmd):
                lex = shlex.split(open(cmd), posix=True)
                args = list(lex) + args
                args[0] = 'pause'
            else:
                print('unknown cmd "%s"' % cmd)

    def utils(self, text):
        if 'type' in text:
            res = text.split(' ')[-1]
            return res

    def get_random(self, i):
        res = round(random.uniform(0.1, 0.2), 2)
        return res

    def produce_vdo(self, **kwargs):
        env.filters['utils'] = self.utils
        env.filters['get_random'] = self.get_random
        tpl = env.get_template(r'./template.txt')
        try:
            with open(kwargs['userpath'] + '/command.vdo', 'w+') as fout:
                render_content = tpl.render(vdo_command=kwargs['commands'])
                fout.write(render_content)
            return True
        except Exception as e:
            return False


@app.route('/api/index', methods=['GET'])
@auth.login_required
def Auth_index():
    auths.client = g.client
    auths.client_screen(g.userpath)
    # html = render_template('automatic.html', src=g.userpath + '/screen.png')
    resp = make_response('html')
    # session['client']=str(client)
    resp.set_cookie('userpath', g.userpath)
    resp.set_cookie('ip', g.ip)
    resp.set_cookie('port', g.port)
    return resp


@auth.verify_password
def verify_password(username, ip):
    ip = request.args.getlist('ip').pop(0)
    port = request.args.getlist('port').pop(0)
    username = request.args.getlist('username').pop(0)
    auths.ip_filter(ip)
    auths.port_filter(port)
    client = api.connect('{}::{}'.format(ip, port))
    user_path = app.config['MYSTATIC'].format(username)
    if not os.path.exists(user_path):
        os.makedirs(user_path)
    g.username = username
    g.ip = ip
    g.port = port
    g.userpath = user_path
    g.client = client
    return True


@app.route('/api/target/<task>', methods=['POST'])
def Target(task):
    userpath = request.cookies.get('userpath')
    ip = request.cookies.get('ip')
    port = request.cookies.get('port')
    client = api.connect('{}::{}'.format(ip, port))
    auths.client = client
    if task == 'chongbo':
        commands = eval(request.form['data'])
        if auths.produce_vdo(commands=commands, userpath=userpath):
            vdo_path = userpath + '/command.vdo'
            try:
                auths.allocate_vncvdo(vdo_path)
            except Exception as e:
                auths.response_filter(0)
            else:
                auths.client_screen(userpath)
                return 'success'
        else:
            auths.response_filter(0)
    else:
        auths.response_filter(1)


auths = Auths()
app.run()
