module.exports = function () {
  console.log('hackDevice disconnect');
  if (game.device_game == 2) {
    console.log(esp_status['hackDevice']);
    if (esp_status['hackDevice'] && esp_status['hackDevice']['finish_2']) {
      esp_action.send('off0', 'air');
      game.device_game = 1
    }
  }
};
