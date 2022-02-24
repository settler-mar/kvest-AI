module.exports = function (code, commands) {
  console.log('hackDevice commands', commands)
  if (commands[0] == 'game') {
    esp_action.send('/game:' + game.device_game)
    if (game.device_game == 1) { //вентиляция
      if (esp_status.air && esp_status.air.st) {
        console.log(esp_status.air)
        esp_action.send('/air:' + esp_status.air.st, 'hackDevice')
      }
    } else if (game.device_game == 2) { // кодовый замок

    }
  }
}