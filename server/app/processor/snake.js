const colors = require('colors');
const fs = require('fs')
//const base_path = require('../../paths.js')['snake']
let hard_level = 2
//chrome --window-position=0,0 --start-fullscreen http://127.0.0.1:8080/game.html

function get_number(str) {
  str = str.match(/(\d+)/)
  if (!str) return 0
  return parseInt(str[0])
}


// esp_action.inner(code, command, ip)
module.exports = function (code) {
  if (code.endsWith('reset')) {
    hard_level = 2
    return
  }

  if (code.endsWith('update')) {
    // console.log(esp_status)
  }
  if (code.indexOf('hard_level') !== -1) {
    hard_level = parseInt(code.split('hard_level')[1]) || 0
  }
  update_file()
}