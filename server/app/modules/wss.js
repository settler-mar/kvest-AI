const WebSocket = require('ws');
const url = require('url');
var WS_clients = [];

module.exports.init = (server, config) => {
  const wss_web = new WebSocket.Server({server});

  global.wss_send = function (part, message) {
    let msg = part + ":" + message;
    for (let i = 0; i < WS_clients.length; i++) {
      WS_clients[i].send(msg);
    }
  }

  wss_web.on('connection', function connection(client) {
    WS_clients.push(client);
    console.log('new client web', WS_clients.length);
    client.on('message', message => {
      console.log("Web command: ",message)

      game_control.processed(message)
    });
    client.on('close', (reasonCode, description) => {
      for (let i = 0; i < WS_clients.length; i++) {
        if (WS_clients[i] == client) {
          WS_clients.splice(i, 1);
          return
        }
      }
    });
  });

  /*wss_esp.on('connection', function connection(client) {
   console.log('new client esp');
   var code = null;
   client.send('get_code')

   client.on('message', 'wss esp', message => console.log(message));
   });*/


  function now() {

    var weekDay = ['воскресенье', 'понедельник', 'вторник', 'среда', 'четверг', 'пятница', 'суббота'];

    var date = new Date();
    var currentDate = weekDay[date.getDay()] + ', ' + textDate(date) + ' ' + textTime(date);

    wss_send('time', currentDate)
  }

  var textDate = function (date) {
    var months = ['января', 'февраля', 'марта', 'апреля', 'мая', 'июня', 'июля', 'августа', 'сентября', 'октября', 'ноября', 'декабря'];
    return date.getDate() + ' ' +
      months[date.getMonth()] + ' ' +
      (date.getFullYear() < 10 ? '0' : '') + date.getFullYear();
  }
  var textTime = function (date) {
    return (date.getHours() < 10 ? '0' : '') + date.getHours() + ':' +
      (date.getMinutes() < 10 ? '0' : '') + date.getMinutes() + ':' +
      (date.getSeconds() < 10 ? '0' : '') + date.getSeconds();
  }

  //передаем текущее веремя
  setInterval(now, 1000);

}