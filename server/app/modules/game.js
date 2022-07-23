global.game = {
  status: 0,
  timer: "",
  time: 0,
  game_time: 60 * 60,
  lang: 'ru',
  device_game: 0
}

global.game_control = {}

let timerGame = null

const timer = require("../../app/processor/timer.js")

function timer_pause() {
  console.log('timer_pause')
  timer('/time/pause')
}

function timer_send() {
  console.log('timer_send')
  timer('/time/' + int_to_time(game.game_time - game.time))
}

module.exports = (config) => {
  fZero = (n) => {
    if (n > 9) return n
    return '0' + n
  }

  int_to_time = (i) => {
    let s = i % 60;
    let m = (i - s) / 60;
    return fZero(m) + ":" + fZero(s)
  }

  update_game = () => {
    game.timer = int_to_time(game.game_time - game.time)
    game.timer += " / " + int_to_time(game.game_time)

    wss_send('game', JSON.stringify(game))
  }

  game_control.pause = () => {
    game.status = 2;
    clearInterval(timerGame)
    update_game()
    timer_pause()
  }

  game_control.addTime = () => {
    game.game_time += 60 * 5
    timer_send()
  }

  game_control.start = () => {
    if (game.status !== 0) {
      game.time = 0;
      esp_action.reset();
      console.log('reset on start')
    }

    if (game.time === 0) {
      esp_action.start();
    }
    game.status = 1;
    game.device_game = 2;
    game.game_time = 60 * 60;

    clearInterval(timerGame);
    timerGame = setInterval(() => {
      game.time++;
      update_game()
    }, 1000)

    //изменяем статус устройств
    setTimeout(() => {
      // включаем порты для хакерского устройства
      esp_action.send('on0', 'air');
      esp_action.send('on1', 'air');
    }, 1000);

    esp_action.wss_send('media','1:doors:ch0')

    update_game();
    timer_send();
  };

  game_control.reset = () => {
    timer_pause()
    game.status = 0;
    game.time = 0;
    esp_action.reset();
    clearInterval(timerGame);
    update_game()
  }

  game_control.stop = () => {
    timer_pause()
    game.status = -1;
    clearInterval(timerGame);
    update_game()
  }

  game_control.lang = (value) => {
    if (['ru', 'ua', 'en'].indexOf(value) < 0) {
      return
    }
    game.lang = value;
    esp_action.lang(value)
    update_game()
  }
  game_control.game = (value) => {
    game.device_game = value;
    update_game()
  }

  game_control.processed = (message) => {
    if (message in game_control) {
      game_control[message]()
      return
    }
    message = message.split(':');
    if (message[0] in game_control) {
      game_control[message[0]](message[1])
      return
    }
    esp_action.do(message[0], message[1])
  }
}
