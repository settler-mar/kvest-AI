module.exports = [
  {
    'code': 'hackDevice',
    'name': 'Хакерское устройство',
    'has_lang': true,
    'processor': require("./app/processor/hackDevice.js"),
    'onDisconnect': require("./app/processor/hackDevice_disconnect.js"),
    'display': false
  },
  {
    'code': 'doors',
    'name': 'Входная дверь',
  },
  {
    'code': 'logo',
    'name': 'Лого'
  },
  {
    'code': 'injectorBox',
    'name': 'Ящик с шприцом',
  },
  {
    'code': 'air',
    'name': 'Система охлождения',
    'processor': require("./app/processor/send_to_hackDevice.js"),
  },
  {
    'code': 'timer',
    'name': 'Таймер',
    'has_lang': true,
    'send': require("./app/processor/timer.js")
  },
  {
    'code': 'gloves0',
    'name': 'Клавиатура основная',
    'processor': require("./app/processor/send_to_hackDevice.js")
  },
  {
    'code': 'gloves1',
    'name': 'Клавиатура дополнительная',
    'processor': require("./app/processor/send_to_hackDevice.js")
  },
];
