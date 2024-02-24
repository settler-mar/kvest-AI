const {spawn} = require('child_process');

function run_process(file_path) {
  console.log('begin process', file_path)
  const proc = spawn('python', [file_path], {
  stdio: 'inherit',
  cwd:'../games/'});
  console.log('process', proc.pid)
}

const script_list = [
    '../games/web_clients.py',
    '--version'
]
module.exports = () => {
  // run_process('test.py')
  script_list.forEach((script) => {
    run_process(script)
  })
}