

module.exports = [
  {
    'code':'hackDevice',
    'name':'Хакерское устройство',
    'has_lang': true,
    'processor': require("./app/processor/hackDevice.js"),
    'status':{
      'game': {
        'title': 'Игра',
        'type':'list',
        'list': {
          1: 'Вентиляция',
        }
      }
    }
  },
  {
    'code':'doors',
    'name':'Входная дверь',
    'commands':{
      'open0': 'Открыть',
      'close0': 'Закрыть',
    },
    'status':{
      'door0': {
        'title': '',
        'type': 'status',
      }
    }
  },
  {
    'code':'logo',
    'name':'Лого',
    'commands':{
      'reset': 'Сброс',
      'start': 'Запуск',
      'finish': 'Завершить',
    },
    'status':{
      'start': {
        'title': 'задача запущенна',
        'type': 'status'
      },
      'input': {
        'title': 'Введенный код',
        'type': 'text'
      },
      'finish': {
        'title': 'задача окончена',
        'type': 'status'
      }
    }
  },
  {
    'code':'doors',
    'name':'Межкомнатная дверь',
    'commands':{
      'open1': 'Открыть',
      'close1': 'Закрыть',
    },
    'status':{
      'door1': {
        'title': '',
        'type': 'status',
      }
    }
  },
  {
    'code':'injectorBox',
    'name':'Ящик с шприцом',
    'commands':{
      'reset': 'Сброс',
      'finish': 'Завершить задание',
    },
    'status':{
      'error':{
        'title':'Состояние',
        'type':'list',
        'list': {
          0: 'все выполнено',
          1: 'вставили флешку',
          2: 'подали питание',
          3: '-'
        }
      },
      'progress':{
        'title':'Шприц',
        'type':'progress',
        'min':0,
        'max':10
      },
      'finish': {
        'title': 'задача окончена',
        'type': 'status',
        'on':['stop']
      }
    }
  },
  {
    'code':'air',
    'name':'Система охлождения',
    'processor': require("./app/processor/air.js"),
    'commands':{
      'reset': 'Сброс',
      'start': 'Начать задание',
    },
    'status':{
      'st': {
        'title': 'Состояние',
        'type': 'text'
      },
    }
  },
  {
    'code':'doors',
    'name':'Дверь к ИИ',
    'commands':{
      'open2': 'Открыть',
      'close2': 'Закрыть',
    },
    'status':{
      'door2': {
        'title': '',
        'type': 'status',
      }
    }
  },
];
