import re
import threading
import json
import bottle

from appmodule import AppModule
from .livecontroller import LiveController


class MyAppModule(AppModule):
    """
        This webapp module add support for << and >> tags
        and implements liveview decorator
    """

    def __init__(self, catchall=True, autojson=True):
        super(MyAppModule, self).__init__(catchall, autojson)
        self.lock = threading.Lock()
        self.vars_templates_map = {}  # template_name:vars_map
        self.live = LiveController(self)

    def _process_live(self, body):
        """
            Parse template for << >> tags
            return body_as_string, vars_map
        """
        vars_map = {}
        str_list = []
        regex = r'<<([^<>]+)>>'
        matches = re.finditer(regex, body, re.MULTILINE)
        pos = 0
        cntid = 0
        for m in matches:
            str_list.append(body[pos:m.start()])
            pos = m.end()
            for groupNum in range(len(m.groups())):
                tag = m.group(groupNum+1).strip()

                if tag.startswith('?'):
                    term = tag[1:].strip()
                    # get variable value from server
                    ix = term.find(' ')
                    if ix == -1:
                        varname = term
                        str_list.append("wsGet('{}');".format(varname))
                    else:
                        varname = term[:ix]
                        default = term[ix:].strip()
                        str_list.append(
                            "wsInit('{0}', {1}); wsGet('{0}');".format(varname, default))

                if tag.startswith('!'):
                    # function call
                    term = tag[1:].strip()
                    ix = term.find(' ')
                    if ix == -1:
                        funcname = term
                        str_list.append("wsCall('{}', null)".format(funcname))
                    else:
                        funcname = term[:ix]
                        args = term[ix:].strip()
                        str_list.append("wsCall('{}', {})".format(funcname, args))

                if tag.startswith('@'):
                    # a js var
                    varname = tag[1:].strip()
                    L = vars_map.get(varname, [])
                    L.append(cntid)
                    vars_map[varname] = L
                    span = '<span id="var{}"></span>'.format(cntid)
                    str_list.append(span)
                    cntid = cntid + 1

        str_list.append(body[pos:])
        return ''.join(str_list), vars_map

    def liveview(self, template_name):
        """
            Decorator function for render live template
        """
        def decorator(func):
            def wrapper(*args, **kwargs):
                # cached in AppModule
                tpltext = self._get_template(template_name)
                if self.module_config.get('module disabled'):
                    return self.err_msg('Error', 'Module disabled by admin')
                else:
                    result = func(*args, **kwargs)
                    if isinstance(result, (dict,)):
                        # if function return a dict, then render a template
                        TEMPLATE_PATH = [
                            self.server_template_folder, self.module_template_folder]
                        template = bottle.SimpleTemplate(
                            tpltext, lookup=TEMPLATE_PATH)
                        # 1 render bottle template => we get populated {{vars}}
                        result.update({'jsvars': '{}'})
                        data = result.copy()
                        self._update_data(data)
                        body = template.render(**data)
                        # 2 render template with live tags => we get vars_map
                        _, vars_map = self._process_live(body)
                        # Compute list of javascript vars used to render html page
                        all_vars = ['\n  var {} = null;'.format(x) for x in vars_map.keys()]
                        jsvars = '{}\n  var jsvars = {};\n'.format(''.join(all_vars), json.dumps(vars_map))
                        result.update({'jsvars': jsvars})
                        with self.lock:
                            self.vars_templates_map[template_name] = vars_map
                        # 3 render again bottle template
                        data = result.copy()
                        self._update_data(data)
                        body = template.render(**data)
                        # 4 render again template with live tags
                        body, _ = self._process_live(body)
                        return body
                    else:
                        return result
            return wrapper
        return decorator


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
