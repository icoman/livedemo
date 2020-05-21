<!-- Live Websocket JavaScript support -->


<script>
  //
  // even if this is just js code
  // it must be included with % include('livews.tpl', url='live')
  // to allow server to parse {jsvars} and {module_name} and {url} 
  //

  var ws = null;
  {{ !jsvars }}

  function getWebsocketUrl(url) {
    pathArray = location.href.split("/");
    protocol = pathArray[0];
    host = pathArray[2];
    console.log(protocol);
    if(protocol == 'http:')
       return `ws://${host}/{{ module_name }}/${url}`;
    else
       return `wss://${host}/{{ module_name }}/${url}`;
  }

  // ws function to call server
  function wsSendVars(ob) {
    ws.send(JSON.stringify({ type: "pub", data: ob }));
  }
  function wsCall(name, args) {
    ws.send(JSON.stringify({ type: "call", data: name, args: args }));
  }
  function wsInit(name, value) {
    ws.send(JSON.stringify({ type: "init", data: name, value: value }));
  }
  function wsGet(name) {
    ws.send(JSON.stringify({ type: "get", data: name }));
  }

  $(document).ready(function () {

    if (!window.WebSocket) {
      if (window.MozWebSocket) {
        window.WebSocket = window.MozWebSocket;
      } else {
        $('#messages').append("<li>Your browser doesn't support WebSockets.</li>");
      }
    }

    ws = new WebSocket(getWebsocketUrl("{{ url }}"));
    
    ws.onopen = function (evt) {
      $('#messages').append('<li>Connected to chat.</li>');
      if (typeof after_connected !== 'undefined') { after_connected(); }
    }

    ws.onclose = function (evt) {
      $('#messages').append('<li>Disconnected from chat.</li>');
    }

    ws.onmessage = function (evt) {
      let ret = JSON.parse(evt.data);
      for (var prop in ret) {
        if (typeof on_message !== 'undefined') { on_message(prop, ret[prop]); }
        else
          live_update(prop, ret[prop]);
      };
    }

  });

  function live_update(name, value) {
    var ids = jsvars[name];
    if (ids) {
      // if `name` is a valid server side variable

      // set local (browser) javascript variable
      eval(`${name} = ${JSON.stringify(value)};`);

      // update div element with jquery
      for (var i = 0; i < ids.length; i++) {
        var obid = '#var' + ids[i];
        $(obid).text(value);
      }
    }
  }


</script>