'use strict';
const url = require('url');
const http = require('http');
const colors = require('colors');
const fs = require('fs');
const ip_file = 'ip_list.data';

global.esp_list = require('../../esp_list');
global.esp_congigs = require('../../esp_congigs');
global.esp_name = {};
global.esp_action = {};
global.esp_status = {};
let esp_callback = {};


var esp_param = ['has_lang', 'processor', 'onDisconnect', 'send'];

fs.readFile(ip_file, (err, data) => {
  let ip_list = err ? {} : JSON.parse(data)
  esp_congigs.forEach(el => {
      esp_name[el.code] = ip_list[el.code] ? {ip: ip_list[el.code]} : {};
      for (let param_name of esp_param) {
        if (el[param_name]) {
          esp_name[el.code][param_name] = el[param_name]
        }
      }
      if (el.status) {
        for (var prop in el.status) {
          if (el.status[prop].on) {
            if (!esp_callback[el.code]) {
              esp_callback[el.code] = {}
            }
            esp_callback[el.code][prop] = el.status[prop].on
          }
        }
      }
    }
  );
  console.log(esp_name)
})

const offlineTimer = 10000;
let esp_timer = {};

const reset_timer = function (code, ip) {
  esp_name[code].ip = ip;
  esp_name[code].online = true;

  var ip_list = {};
  for (const [key, value] of Object.entries(esp_name)) {
    if (value && value.ip) {
      ip_list[key] = value.ip
    }
  }

  fs.writeFile(ip_file, JSON.stringify(ip_list), () => {
  });

  if (esp_timer[code]) {
    clearTimeout(esp_timer[code])
  }

  esp_timer[code] = setTimeout(function (code) {
    esp_name[code]['online'] = false;
    wss_send('esp_list', JSON.stringify(esp_name));

    if (esp_name[code]['onDisconnect']) {
      esp_name[code]['onDisconnect']()
    }
  }, offlineTimer, code);

  wss_send('esp_list', JSON.stringify(esp_name))
}

const sendEsp = (path, code, test_property)=> {
  const send = (path, code, test_property)=> {
    // console.log('>', code, path)
    if (!!esp_name[code]) {
      if (test_property && !esp_name[code][test_property]) {
        return
      }

      if (esp_name[code]['send']) {
        esp_name[code]['send'](path)
      } else {
        http.request({host: esp_name[code].ip, path}).on('error', (e) => {
          //console.error(`problem with request: ${e.message}`);
        }).end();
      }
    } else {
      //console.log(code,'is offline')
    }
  };

  if (code) {
    send(path, code, test_property)
  } else {
    for (var code in esp_name) {
      send(path, code, test_property)
    }
  }
};

esp_action.send = sendEsp;

esp_action.reset = ()=> {
  console.log('esp reset');
  esp_status = {};
  wss_send('status', JSON.stringify(esp_status));
  sendEsp('/reset')
}

esp_action.start = ()=> {
  console.log('esp start');
  sendEsp('/start')
}

esp_action.do = (code, event)=> {
  console.log('esp do', event);
  sendEsp('/' + event, code)
}
esp_action.lang = (lang) => {
  console.log('esp lang', lang);
  sendEsp('/lang/' + lang, false, 'has_lang')
}


module.exports = (router, config) => {
  router.get("/esp/*", (req, res) => {
      const pathname = url.parse(req.url).pathname;
      const code = pathname.split('/')[2];
      let command = req.header('X-COMMAND') || req.header('x-command') || req.query['command'] || pathname.split('/')[3] || '';
      // console.log(req.header('X-COMMAND') || req.header('x-command'));
      // console.log(req.headers)
      const ip = req.query['ip'] || req.params['ip'] || req.clientIp.split(':').pop();

      command = command.split(':');
      console.log(colors.green(code), colors.yellow(ip), command);

      if (!esp_name.hasOwnProperty(code)) {
        res.send('err');
        return
      }
      reset_timer(code, ip);

      if (command.length < 2) {
        command[1] = 1
      }
      // if (command[0] == 'start') {
      //   esp_status[code] = {}
      // } else
      if (command[0] == 'lang') {
        sendEsp('/lang/' + game.lang, code)
      } else if (command[0] == 'reset_game') {
        game_control.stop()
        game_control.reset()
      }
      else if (command[0] == 'start_game') {
        game_control.start()
      } else {
        if (!esp_status[code]) {
          esp_status[code] = {}
        }
        esp_status[code][command[0]] = command[1] || true;
      }

      if (esp_name[code]['processor']) {
        esp_name[code]['processor'](code, command)
      }

      if (esp_callback[code] && esp_callback[code][command[0]]) {
        esp_callback[code][command[0]].forEach(cmd => {
          game_control.processed(cmd)
        })
      }
      wss_send('status', JSON.stringify(esp_status));

      res.send('ok')
    },
  );
};