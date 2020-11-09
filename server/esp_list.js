module.exports = [
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
