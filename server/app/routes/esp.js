'use strict';
const url = require('url');
const http = require('http');
const colors = require('colors');
const fs = require('fs');
const ip_file='ip_list.data'

global.esp_list = require('../../esp_list');
global.esp_name = {}
global.esp_action = {}
global.esp_status = {}
let esp_calback = {}



fs.readFile(ip_file, (err, data) => {
  let ip_list = err ? {} : JSON.parse(data)
  esp_list.forEach(el => {
      esp_name[el.code] = ip_list[el.code] ? {ip: ip_list[el.code]} : null
      if (el.status) {
        for (var prop in el.status) {
          if (el.status[prop].on) {
            if (!esp_calback[el.code]) {
              esp_calback[el.code] = {}
            }
            esp_calback[el.code][prop] = el.status[prop].on
          }
        }
      }
    }
  );
})

const offlineTimer = 10000;
let esp_timer = {}

const reset_timer = function (code, ip) {
  esp_name[code] = {
    "ip": ip,
    "online": true
  };
  var ip_list = {}
  for (const [key, value] of Object.entries(esp_name)) {
    if (value && value.ip) {
      ip_list[key] = value.ip
    }
  }

  fs.writeFile(ip_file, JSON.stringify(ip_list),() => {});

  if (esp_timer[code]) {
    clearTimeout(esp_timer[code])
  }

  esp_timer[code] = setTimeout(function (code) {
    esp_name[code]['online'] = false;
    wss_send('esp_list', JSON.stringify(esp_name));
  }, offlineTimer, code);

  wss_send('esp_list', JSON.stringify(esp_name))
}

const sendEsp = (path, code)=> {
  const send = (path, code)=> {
    if (!!esp_name[code]) {
      http.request({host: esp_name[code].ip, path}).on('error', (e) => {
        //console.error(`problem with request: ${e.message}`);
      }).end();
    } else {
      //console.log(code,'is offline')
    }
  }

  if (code) {
    send(path, code)
  } else {
    for (var code in esp_name) {
      send(path, code)
    }
  }
}

esp_action.reset = ()=> {
  console.log('esp reset')
  esp_status = {}
  wss_send('status', JSON.stringify(esp_status));
  sendEsp('/reset')
}

esp_action.start = ()=> {
  console.log('esp start')
  sendEsp('/start')
}

esp_action.do = (code, event)=> {
  console.log('esp do', event)
  sendEsp('/' + event, code)
}

module.exports = (router, config) => {
  router.get("/esp/*", (req, res) => {
      const pathname = url.parse(req.url).pathname;
      const code = pathname.split('/')[2];
      let command = req.header('X-COMMAND') || req.query['command'] || pathname.split('/')[3] || '';
      const ip = req.query['ip'] || req.params['ip'] || req.clientIp.split(':').pop()

      command = command.split(':')
      console.log(colors.green(code), colors.yellow(ip), command);

      if (!esp_name.hasOwnProperty(code)) {
        res.send('err');
        return
      }
      reset_timer(code, ip);

      if (command[0] == 'start') {
        esp_status[code] = {}
      } else {
        if (!esp_status[code]) {
          esp_status[code] = {}
        }
        esp_status[code][command[0]] = command[1] || true;
      }

      if (esp_calback[code] && esp_calback[code][command[0]]) {
        esp_calback[code][command[0]].forEach(cmd => {
          game_control.processed(cmd)
        })
      }
      wss_send('status', JSON.stringify(esp_status));

      res.send('ok')
    },
  );
};