% include('header.tpl')

% include('livews.tpl', url='live')

<h1>{{title}}</h1>

<table class="table">
  <tr>
    <td>
      <h1><<@servertime>> cnt=<<@cnt>> <<@operation>> </h1>

      <button class="btn btn-success" onclick="<<!enable_clock_thread>>">Enable Clock</button>
      <button class="btn btn-warning" onclick="<<!disable_clock_thread>>">Disable Clock</button>
      <button class="btn btn-primary" id="inc">+</button>
      <button class="btn btn-primary" id="dec">-</button>

      <h3 class="pull-right"><<@servertime>></h3>

      <br>
      <font size="+2">cnt:</font>
      %for i in ['#acf','#f00','#000','#faa']:
      <font size="+2" color="{{i}}">
        <<@cnt>>
      </font>
      %end

    </td>
    <td width="50"></td>
    <td nowrap>
      <form id="chatform" class="form form-inline">
        <div class="form-group">
          <label>Name: <input id="name" type="text" value="{{userfullname}}"></label>
          <label>Color:
            <select id="color">
              %for i in ('#000','#f00','#0f0','#00f','#acf'):
              <option style="color: {{i}}" value="{{i}}">{{i}}</option>
              %end
            </select>    
          </label>
        </div>
        <br>
        <div class="form-group">
          <label>
            Message:
            <input id="message" type="text" value="Hello!">
            <input type="submit" value="Send" class="btn btn-primary" />
            <input type="button" value="Clear" id="btnclr" class="btn btn-warning" />
          </label>
        </div>
      </form>
      <div id="messages" class="well"></div>

    </td>
  </tr>
</table>



<script>

  function after_connected() {
    //
    // init vars on server side and update clients
    // it is safe if this function is not defined
    // 
    << ? cnt  2000  >> << ? operation >>
    <<   ? servertime    '-time-' >>
  }

  function on_message(key, value) {
    //
    // this function is called when
    // a message comes from the server
    //
    if (key == 'chatmsg')
      // append to chat 
      $('#messages').append('<li>' + value + '</li>');
    else
      // update web page
      live_update(key, value);
  }

  $("#btnclr").off().click(function () {
    $('#messages').empty();
    $('#message').focus();
  });

  $("#inc").off().click(function () {
    cnt = cnt + 1;
    wsSendVars({ cnt: cnt, operation: 'counter inc'});
  });

  $("#dec").off().click(function () {
    cnt = cnt - 1;
    wsSendVars({ cnt: cnt, operation: 'counter dec'});
  });




  $('#chatform').submit(function () {
    var name = $('#name').val();
    var message = $('#message').val();
    var color = $('#color').val();
    if(message.length>0)
      wsSendVars({ chatmsg: `${name}: <font color="${color}">${message}` });
    $('#message').val('').focus();
    return false;
  });

  $('#color').change(function () {
      console.log('sch color');
      var color = $('#color').val();
      $("#color").css({ "backgroundColor": "white", "color": color});
  });

</script>

% include('footer.tpl')