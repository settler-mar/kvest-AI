'use strict';
const url = require('url');
var http = require('http');

global.esp_list = require('../../esp_list');
global.esp_name = {}
global.esp_action = {}

esp_list.forEach(el => {
    esp_name[el.code] = null
  }
);

const offlineTimer = 5000;
let esp_timer = {}

const reset_timer = function(code, ip){
  esp_name[code] = {
    "ip": ip,
    "online": true
  };

  if(esp_timer[code]){
    clearTimeout(esp_timer[code])
  }

  esp_timer[code] = setTimeout(function (code) {
    esp_name[code]['online'] = false;
    wss_send('esp_list',JSON.stringify(esp_name));
  },offlineTimer,code);

  wss_send('esp_list',JSON.stringify(esp_name))
}

const sendEsp = (path, code)=>{
  const send = (path, code)=>{
    if(esp_name[code]){
      http.request({host:esp_name[code].ip,port:9000,path}).end();
    }else{
      console.log(code,'is offline')
    }
  }

  if(code){
    send(path, code)
  }else {
    for (var code in esp_name) {
      send(path, code)
    }
  }
}

esp_action.reset = ()=>{
  console.log('esp reset')
  sendEsp('/reset')
}

esp_action.start = ()=>{
  console.log('esp start')
  sendEsp('/start')
}

esp_action.do = (event)=>{
  console.log('esp do',event)
  sendEsp('/do?do='+event)
}

module.exports = (router, config) => {
  router.get("/esp/*",(req, res) => {
    const pathname = url.parse(req.url).pathname;
    const code = pathname.split('/')[2];
    const ip = req.clientIp.split(':').pop()

    if(code=="start"){
      res.send('ok')
      http.request({host:ip,path:"/getName"}).end();
      return;
    }

    if (!esp_name.hasOwnProperty(code)){
      res.send('err')
      return
    }
    reset_timer(code,ip)

    res.send('ok')
    },
  );
};