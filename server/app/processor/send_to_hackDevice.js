module.exports = function (code, commands) {
  console.log(code + ' commands', commands ,' send to hack');
  if ((commands[0] == 'st') || (commands[0] == 'btn')) {
    esp_action.send('/' + code + ':' + commands[1], 'hackDevice')
  }
}
