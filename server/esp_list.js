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
      'login': {
        'title': 'Пароль',
        'type': 'status'
      },
    }
  },
  {
    'code': 'snake',
    'name': 'Змейка',
    'status': {
      'hard_level': {
        'title': 'Сложность',
        'type': 'select',
        'list': [1, 2, 3]
      },
      'foods': {
        'title': 'Еда',
        'type': 'text'
      },
      'level': {
        'title': 'Пройдено уровней',
        'type': 'text'
      },
      'finish': {
        'title': 'задача окончена',
        'type': 'status'
      }
    }
  },
  {
    'code': 'logo',
    'name': 'Лого',
    'commands': {
      'reset': 'Сброс',
      'run': 'Запуск',
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
    'code': 'snake',
    'name': "Документация",
    'status': {
      'unbugged': {
        'title': 'Доументация',
        'type': 'status'
      },
      'manual_electricity': {
        'title': 'Electricity Data',
        'type': 'status'
      },
      'autonomy': {
        'title': 'Autonomy AI power',
        'type': 'status'
      },
      'project': {
        'title': 'Project changes',
        'type': 'status'
      },
      'safety': {
        'title': 'Safety Instruction',
        'type': 'status'
      },
      'operating': {
        'title': 'Operating system upgrade',
        'type': 'status'
      },
      'working': {
        'title': 'Project failure protection',
        'type': 'status'
      }
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
      'down': 'Опустить',
      'up': 'Поднять',
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
      'lift': {
        'title': 'Лифт',
        'type': 'list',
        'list': {
          0: 'вверх (движение)',
          1: 'вниз (движение)',
          2: 'вверху',
          3: 'внизу'
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
