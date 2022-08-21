const exec = require('child_process').execFile;

const fs = require('fs')
const base_path = require('../../paths.js')['snake']
let hard_level = 2


function get_number(str) {
  str = str.match(/(\d+)/)
  if (!str) return 0
  return parseInt(str[0])
}

const update_file = () => {
  let content = game.lang + "\n" + hard_level
  fs.writeFile(base_path + 'SnakeIN.txt', content, {flag: 'w'}, err => {
  })
}

const run_game = () => {
  update_file()
  fs.writeFile(base_path + 'GamePhase.txt', 'Start', {flag: 'w'}, err => {
  })
  try {
    fs.unlinkSync(base_path + 'SnakeOUT.txt')
  } catch (err) {
    console.error(err)
  }
  if (fs.existsSync(base_path + 'Snake2022.exe')) {
    exec(base_path + 'Snake2022.exe', {'cwd': base_path})
  }
}

fs.watchFile(base_path + 'SnakeOUT.txt', function (event, filename) {
  console.log('SnakeOUT.txt change');
  fs.readFile(base_path + 'SnakeOUT.txt', 'utf8', (err, data) => {
    if (err) {
      console.error(err);
      return;
    }
    let result = {'level': 0}
    for (let line of data.split('\n')) {
      if (line.indexOf('Electricity Data read') !== -1) result['manual_electricity'] = 1
      if (line.indexOf('Login successful') !== -1) result['login'] = 1
      if (line.indexOf('Restarting with result') !== -1) result['foods'] = get_number(line)
      if (line.indexOf('All info unbugged') !== -1) result['unbugged'] = 1
      if (line.indexOf('Difficulty') !== -1) result['hard_level'] = 1
      if (line.indexOf('Level') !== -1 && line.indexOf('complete')) result['level'] = Math.max(result['level'], get_number(line))
      if (result['level'] === 4) result['finish'] = 1

      if (line.indexOf('User reads panel') !== -1) {
        if (line.indexOf('Autonomy AI power') !== -1) result['autonomy'] = 1
        if (line.indexOf('Project changes') !== -1) result['project'] = 1
        if (line.indexOf('Safety Instruction') !== -1) result['safety'] = 1
        if (line.indexOf('Operating system upgrade') !== -1) result['operating'] = 1
        if (line.indexOf('Project failure protection') !== -1) result['project'] = 1
        if (line.indexOf('Working with information') !== -1) result['working'] = 1
      }
    }

    esp_action.inner('snake', ['hard_level', hard_level])
    // esp_status['snake']
    for (let key in result) {
      if (!(key in esp_status['snake']) || esp_status['snake'][key] !== result[key]) {
        esp_action.inner('snake', [key, result[key]])
      }
    }
    console.log(data.split('\n'));
  });
});

// esp_action.inner(code, command, ip)
module.exports = function (code) {
  if (code.endsWith('reset')) {
    hard_level = 2
    esp_action.inner('snake', ['hard_level', hard_level])
    fs.writeFile(base_path + 'GamePhase.txt', 'End\n', function (event, filename) {
    })
    setTimeout(run_game, 5000)
    return
  }
  if (code.indexOf('hard_level') !== -1) {
    hard_level = parseInt(code.split('hard_level')[1]) || 0
  }
  update_file()
}
run_game()