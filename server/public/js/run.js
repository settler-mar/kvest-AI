var base_url = location.protocol + '//' + location.hostname + (location.port != 80 ? ':' + location.port : '');
var ws = false;
var ws_timer = false;
var animationEnd = 'webkitAnimationEnd mozAnimationEnd MSAnimationEnd oanimationend animationend';
var ws_error = 0

document.addEventListener("DOMContentLoaded", function (event) {
  ws_start();
});

function ws_start() {
  if (ws) {
    ws.close();
    ws.onclose = function () {
    };
    ws.onopen = function () {
    };
    ws.onerror = function () {
    };
    ws.onmessage = function () {
    };
    ws.terminate()
    console.log('kill ws')
  }

  ws = new WebSocket(base_url.replace('http', 'ws'))
  clearInterval(ws_timer);
  ws_timer=setInterval(ws_start,2000);

  ws.onopen = function () {
    console.log('WebSocket Connect');
    clearInterval(ws_timer);
  };

  ws.onerror = function (error) {
    console.log('WebSocket Error ', error);
    ws_error++
    if (ws_error > 600)ws_error = 600
    clearInterval(ws_timer);
    ws_timer=setInterval(ws_start,1000+ws_error*100);
  };

  ws.onclose = function () {
    console.log('WebSocket connection closed');
    ws_error++
    if (ws_error > 600)ws_error = 600
    clearInterval(ws_timer);
    ws_timer=setInterval(ws_start,1000+ws_error*100);
  };

  ws.onmessage = function (e) {
    data = e.data.split(':')
    key = data.shift()
    data = data.join(':')


    if (key == 'time') {
      app.time = data
      return
    }

    if (key == 'esp_list') {
      app.esp_list = JSON.parse(data)
      return
    }

    if (key == 'game') {
      app.game = JSON.parse(data)
      return
    }

    if (key == 'game_time') {
      app.game_time = data
      return
    }
    if (key == 'status') {
      app.status = JSON.parse(data)
      return
    }

    console.log(key,data)
  }
}

async function getDataDb(url) {
  /*const response = await fetch(url);
   const data = await response.json();
   app.db[data.year][data.month] = data.list
   app.list = getList()
   app.loading = false
   app.year = typeof (app.year) == 'string' ? app.year * 1 : app.year + "";*/
}


function getList() {
  //выбор данных за нужный месяц
  /*var data = app.db[app.year][app.month];

   var start = (app.showPage - 1) * app.showCount;
   var end = app.showPage * app.showCount;
   //пагинация
   return data.slice(start, end)*/
}