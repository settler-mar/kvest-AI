const {spawn} = require('child_process');

function run_process(file_path) {
  console.log('begin process', file_path)
  const proc = spawn('python3', [file_path], {stdio: 'inherit'});
  console.log('process', proc.pid)
}

const script_list = [
  '../games/web_clients.py',
]
module.exports = () => {
  // run_process('test.py')
  script_list.forEach((script) => {
    run_process(script)
  })
}