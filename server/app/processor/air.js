module.exports = function (code, commands) {
  console.log('air commands',commands)
  if (commands[0]=='st'){
    esp_action.send('/air:'+commands[1], 'hackDevice')
  }
}