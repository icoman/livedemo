
import threading
import json
import bottle


class LiveController(object):

    def __init__(self, app):
        self.app = app
        self.lock = threading.Lock()
        self.clients = set()
        self.funcs = {}  # name:object
        self.vars = None

    def add(self, wsclient):
        """
            Add a websocket client
        """
        with self.lock:
            self.clients.add(wsclient)

    def register_func(self, wsclient, func, name):
        """
            Register a server side function
        """
        with self.lock:
            d = self.funcs.get(wsclient, {})
            d[name] = func
            self.funcs[wsclient] = d

    def broadcast(self, data):
        """
            Send update to all clients
        """
        for c in self.clients:
            c.send(json.dumps(data))

    def run(self, wsclient):
        """
            loop until client disconnect
            deal with message types
        """
        if self.vars is None:
            # update vars before run
            vars = {}
            for _, v in self.app.vars_templates_map.items():
                for name in v.keys():
                    vars[name] = None
            with self.lock:
                self.vars = vars
        while True:
            data = wsclient.receive()
            if data is None:
                # client disconnected
                break

            # expect json data to be a python dict
            msg = json.loads(data)
            msg_type = msg.get('type')
            data = msg.get('data')

            if msg_type == "get":
                self.broadcast({data: self.vars.get(data)})

            if msg_type == "init":
                value = msg.get('value')
                if not self.vars.get(data):
                    with self.lock:
                        self.vars[data] = value

            if msg_type == "pub":
                with self.lock:
                    for k, v in data.items():
                        self.vars[k] = v
                self.broadcast(data)

            if msg_type == "call":
                func = self.funcs.get(wsclient, {}).get(data)
                if func:
                    #print('call', id(func))
                    func()
                else:
                    print('No function to call')

        # client disconnected
        with self.lock:
            self.clients.remove(wsclient)
            try:
                del self.funcs[wsclient]
            except:
                pass

    def add_task(self, func, args):
        t = threading.Thread(target=func, kwargs=args)
        t.daemon = True
        t.start()


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
