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
    'processor': require("./app/processor/air.js"),
  },
  {
    'code': 'timer',
    'name': 'Таймер',
    'send': require("./app/processor/timer.js")
  }
];
