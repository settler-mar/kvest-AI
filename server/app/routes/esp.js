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


var esp_param = ['has_lang', 'processor', 'onDisconnect', 'send', 'onStatus'];

fs.readFile(ip_file, (err, data) => {
  let ip_list = {}
  try {
    ip_list = err ? {} : JSON.parse(data)
  } catch (e) {
    ip_list = ip_list || {}
  }
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

const sendEsp = (path, code, test_property) => {
  const send = (path, code, test_property) => {
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
    for (let code in esp_name) {
      send(path, code, test_property)
    }
  }
};

esp_action.send = sendEsp;

esp_action.reset = () => {
  wss_send('command', 'reset')
  esp_status = {};
  for (let ctrl of esp_list) {
    for (let param in ctrl['status']) {
      if (typeof ctrl['status'][param]['default'] != "undefined") {
        esp_status[ctrl['code']] = {}
        esp_status[ctrl['code']][param] = ctrl['status'][param]['default']
      }
    }
  }
  wss_send('status', JSON.stringify(esp_status));
  sendEsp('/reset')
}

esp_action.start = () => {
  wss_send('command', 'start')
  console.log(colors.cyan('esp start'));
  sendEsp('/start')
}

esp_action.do = (code, event) => {
  console.log(colors.cyan('esp do '), code, '>', event);
  sendEsp('/' + event, code)
}

esp_action.lang = (lang) => {
  console.log(colors.cyan('esp lang'), lang);
  sendEsp('/lang/' + lang, false, 'has_lang')
}

esp_action.inner = (code, command, ip = 'app') => {
  console.log(colors.green(code), colors.yellow(ip), command);

  if (!esp_name.hasOwnProperty(code)) {
    return false
  }
  reset_timer(code, ip);

  if (command.length < 2) {
    command[1] = 1
  }
  let do_start = false
  for (let el of esp_list) {
    if (!do_start) {
      if (el['code'] === code) {
        if (command[0] === ('finish_cmd' in el ? el['finish_cmd'] : 'finish')) {
          do_start = true
          continue
        }
      }
    } else {
      let start_cmd = 'start_cmd' in el ? el['start_cmd'] : 'run'
      if (el['commands'] && start_cmd in el['commands']) {
        console.log(colors.cyan('run next'), el['code'])
        sendEsp(start_cmd, el['code']);
        if (!('skip_on_start' in el)) {
          break
        }
      }
    }
  }
  // if (command[0] == 'start') {
  //   esp_status[code] = {}
  // } else
  if (command[0] === 'lang') {
    sendEsp('/lang/' + game.lang, code)
  } else if (command[0] === 'game') {
    sendEsp('/game/' + game.device_game, code)
  } else if (command[0] === 'reset_game') {
    game_control.stop()
    game_control.reset()
  } else if (command[0] === 'start_game') {
    game_control.start()
  } else if (command[0] === 'prestart_game') {
    esp_action.start();
  } else {
    if (!esp_status[code]) {
      esp_status[code] = {}
    }
    esp_status[code][command[0]] = command[1] || true;
  }
  if (esp_name[code]['onStatus']
    && esp_name[code]['onStatus'][command[0]]
    && esp_name[code]['onStatus'][command[0]][command[1]]) {
    var cmd = [...esp_name[code]['onStatus'][command[0]][command[1]]]
    if (typeof cmd[0] === 'string') {
      cmd = [cmd]
    }
    for (let cm of cmd) {
      if (esp_name[cm[0]]) {
        sendEsp(...cm.reverse())
      }
      wss_send(...cm)
    }
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

      if (esp_action.inner(code, command, ip)) {
        res.send('ok')
      } else {
        res.send('err');
      }
    },
  );
};