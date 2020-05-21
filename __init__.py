#
# Python LiveView Demo
#


import os
import time
import bottle
import datetime
import threading
from bottle.ext.websocket import websocket

from .myappmodule import MyAppModule

app = MyAppModule()


def update_app(module_name, server_config):
    app.update(module_name, server_config)


@app.route('/')
@app.auth('access module')
@app.liveview('index.tpl')
def _():
    """
        Default view
    """
    title = 'Websocket Live Demo'
    bs = app.get_beaker_session()
    userid = int(bs.get('userid', 0))
    userfullname = bs.get('userfullname', 'Anonymous')
    #now = datetime.datetime.now().strftime('%H:%M:%S')
    return dict(title=title, userid=userid, userfullname=userfullname)


@app.get('/live', apply=[websocket])
@app.auth('ws access')
def _(ws):

    if ws is None:
        print('websocket is None')
        return

    app.live.add(ws)

    class Container():
        pass

    bs = app.get_beaker_session()
    userid = int(bs.get('userid', 0))
    if userid == 1:
        # user is admin
        ob = Container()
        ob.runUpdate = False

        def clock_thread(args):
            print('clock_thread({})'.format(args))
            ob.runUpdate = args
            if not ob.runUpdate:
                app.live.broadcast({'servertime': ''})

        def test_func(args):
            print('test_func({}), type(args)={}'.format(args, type(args)))

        def thread1(ob, ws):
            # run thread while client is connected
            while ws in app.live.clients:
                time.sleep(1)
                if ob.runUpdate:
                    now = datetime.datetime.now()
                    hms = now.strftime('%H:%M:%S')
                    app.live.broadcast({'servertime': hms})
            print('thread1 ends')

        app.live.register_func(ws, clock_thread, 'endis_clock_thread')
        app.live.register_func(ws, test_func, 'test')
        app.live.add_task(thread1, {'ob': ob, 'ws':ws})
    app.live.run(ws)


"""

MIT License

Copyright (c) 2020 Ioan Coman

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

"""
