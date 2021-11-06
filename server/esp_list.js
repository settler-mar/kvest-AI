module.exports = [
  {
    'code': 'doors',
    'name': 'Входная дверь',
    'commands': {
      'open0': 'Открыть',
      'close0': 'Закрыть',
      'ch0': 'Вкл/выкл подсветка',
    },
    'status': {
      'door0': {
        'title': '',
        'type': 'status',
      },
      'digital0': {
        'title': 'подсветка',
        'type': 'status'
      },
    }
  },
  {
    'code': '_',
    'name': 'Название игры',
    'status': {
      'start': {
        'title': '',
        'type': 'text'
      },
    }
  },
  {
    'code': '_',
    'name': 'Змейка',
    'status': {
      'start': {
        'title': 'Уровень',
        'type': 'text'
      },
    }
  },
  {
    'code': 'logo',
    'name': 'Лого',
    'commands': {
      'reset': 'Сброс',
      'start': 'Запуск',
      'finish': 'Завершить',
    },
    'status': {
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
    'code': 'air',
    'name': 'Питание. Шкаф замка',
    'status': {
      'pulse0': {
        'title': 'Замок',
        'type': 'status'
      },
      'digital0': {
        'title': 'Порт устройства',
        'type': 'status'
      }
    },
    'commands': {
      'relay0': 'Открыть замок',
      'ch0': 'Вкл/выкл порт',
    }
  },
  {
    'code': 'hackDevice',
    'name': 'Кодовый замок',
    'commands': {
      // 'reset': 'Сброс',
      // 'start': 'Начать задание',
    },
    'status': {
      'code_r': {
        'title': 'Код двери',
        'type': 'text'
      },
      'code_p': {
        'title': 'Введенный код',
        'type': 'text'
      },
      'finish_2': {
        'title': 'задача окончена',
        'type': 'status'
      }
    }
  },
  {
    'code': 'doors',
    'name': 'Межкомнатная дверь',
    'commands': {
      'open1': 'Открыть',
      'close1': 'Закрыть',
    },
    'status': {
      'door1': {
        'title': '',
        'type': 'status',
      }
    }
  },
  {
    'code': 'timer',
    'name': 'Управление спутниками',
    'status': {
      'hand': {
        'title': '',
        'type': 'status',
      },
    },
    'commands': {
      'hand/0': 'Отключить',
      'hand/1': 'Включить',
    },
  },
  {
    'code': '_',
    'name': 'Спутники',
    'status': {
      'start': {
        'title': 'Захваченно спутников',
        'type': 'text'
      },
    }
  },
  {
    'code': 'hackDevice',
    'commands': {
      // 'reset': 'Сброс',
      // 'start': 'Начать задание',
    },
    'status': {
      'code_s': {
        'title': 'Код',
        'type': 'gloves'
      },
      'code_g': {
        'title': 'Введенный',
        'type': 'gloves'
      },
      'finish_3': {
        'title': 'задача окончена',
        'type': 'status'
      }
    }
  },
  {
    'code': 'injectorBox',
    'name': 'Ящик с шприцом',
    'commands': {
      'reset': 'Сброс',
      'finish': 'Завершить задание',
    },
    'status': {
      'error': {
        'title': 'Состояние',
        'type': 'list',
        'list': {
          0: 'все выполнено',
          1: 'вставили флешку',
          2: 'подали питание',
          3: '-'
        }
      },
      'progress': {
        'title': 'Шприц',
        'type': 'progress',
        'min': 0,
        'max': 10
      },
      'finish': {
        'title': 'задача окончена',
        'type': 'status',
        'on': ['stop']
      }
    }
  },
  {
    'code': 'air',
    'name': 'Питание. Шкаф венитиляции',
    'status': {
      'pulse1': {
        'title': 'Замок',
        'type': 'status'
      },
      'digital1': {
        'title': 'Порт устройства',
        'type': 'status'
      }
    },
    'commands': {
      'relay1': 'Открыть замок',
      'ch1': 'Вкл/выкл порт',
    }
  },
  {
    'code': 'air',
    'name': 'Система охлождения',
    'commands': {
      'reset': 'Сброс',
      'start': 'Начать задание',
    },
    'status': {
      'st': {
        'title': 'Состояние',
        'type': 'text'
      },
    }
  },
  {
    'code': 'doors',
    'name': 'Дверь к ИИ',
    'commands': {
      'open2': 'Открыть',
      'close2': 'Закрыть',
    },
    'status': {
      'door2': {
        'title': '',
        'type': 'status',
      }
    }
  },
];
