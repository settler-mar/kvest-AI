module.exports = function (code, commands) {
  console.log('hackDevice commands',commands)
  if (commands[0]=='game'){
    if(commands[1]==1){
      if(esp_status.air && esp_status.air.st) {
        console.log(esp_status.air)
        esp_action.send('/air:' + esp_status.air.st, 'hackDevice')
      }
    }
  }
}