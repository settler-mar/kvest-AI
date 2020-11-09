global.game = {
  status: 0,
  timer: "",
  time: 0
}

global.game_control = {}

let timerGame = null

module.exports = (config) => {
  fZero = (n)=> {
    if (n > 9) return n
    return '0' + n
  }

  update_game = ()=> {
    let s = game.time % 60;
    let m = (game.time - s) / 60;
    game.timer = fZero(m) + ":" + fZero(s)
    wss_send('game', JSON.stringify(game))
  }

  game_control.pause = ()=> {
    game.status = 2;
    clearInterval(timerGame)
    update_game()
  }

  game_control.start = ()=> {
    if (game.status = 0) {
      game.time = 0;
      esp_action.reset();
    }

    if (game.time == 0) {
      esp_action.start();
    }
    game.status = 1;

    clearInterval(timerGame)
    timerGame = setInterval(()=> {
      game.time++;
      update_game()
    }, 1000)

    update_game()
  }

  game_control.reset = ()=> {
    game.status = 0;
    game.time = 0;
    esp_action.reset();
    clearInterval(timerGame);
    update_game()
  }

  game_control.stop = ()=> {
    game.status = 0;
    clearInterval(timerGame);
    update_game()
  }
  game_control.processed = (message)=> {
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
