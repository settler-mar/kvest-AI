const {SerialPort, ReadlineParser} = require('serialport')

let listOfPorts = [];
let last_port = null
let port = null
const app = "hackDevice"
let rssi = ""
let last_send = null
let command_queue = []

function find_connect() {
  setTimeout(find_connect, 5000)
  if (!port || !port.isOpen || !port.status) {
    if (port && port.isOpen) {
      port.close()
    }
    if (esp_action) esp_action.inner(app, [], "scan")
    SerialPort.list().then(get_port_list)
  }
}

function get_port_list(ports) {
  listOfPorts = [];
  for (let port of ports) {
    if (!port || !port.vendorId || port.vendorId.toLowerCase() !== '10c4' ||
      !port.productId || port.productId.toLowerCase() !== 'ea60') continue
    listOfPorts.push(port.path)
  }
  if (!listOfPorts.length) return
  let is_find = false
  console.log('last port', last_port)
  for (let i in listOfPorts) {
    console.log('test', listOfPorts[i], last_port === listOfPorts[i])
    if (last_port === listOfPorts[i]) {
      is_find = true
      continue
    }
    if (is_find) {
      try_connect(listOfPorts[i])
      return
    }
  }
  try_connect(listOfPorts[0])
}

function try_connect(path) {
  last_port = path
  console.log('try_connect', path)
  port = new SerialPort({path, baudRate: 115200})

  port.write('ping', function (err) {
    if (err) {
      if (esp_action) esp_action.inner(app, [], "error")
      return console.log('Error on write: ', err.message)
    }
  })

  port.on('error', function (err) {
    console.log('Error: ', err.message)
    if (esp_action) esp_action.inner(app, [], "error")
    this.status = 0
  })

  port.on('open', function () {
    console.log('open', this.path)
  })

  const parser = new ReadlineParser({delimiter: '\n'})
  port.pipe(parser)
  parser.on('data', data => {
    data = data.trim()
    if (data.indexOf('pong') === 0) {
      port.status = 1
      if (esp_action) esp_action.inner(app, [], port.path)
      return
    }
    // if (esp_action) esp_action.inner(app, [], port.path)
    if (data.indexOf('RSSI') !== -1) {
      data = data.split(':')
      rssi = ':' + data[1]
      return;
    }
    if (data.indexOf('Message') !== -1) {
      data = data.split(':')
      data.shift()
      esp_action.inner(app, data, `${port.path}${rssi}`)
      return;
    }
  })
}

setTimeout(find_connect, 5000)

function processor(code, commands) {
  console.log('hackDevice commands', commands, game.device_game)
  if (commands[0] === 'game') {
    if (parseInt(game.device_game) === 1) { //вентиляция
      console.log(esp_status)
      if (esp_status.air && esp_status.air.st) {
        esp_action.send('/air:' + esp_status.air.st, 'hackDevice')
      }
    } else if (parseInt(game.device_game) === 2) { // кодовый замок

    }
  }
}

function queue_process() {
  setTimeout(queue_process, 100)
  if (!command_queue.length) return

  let code = command_queue.shift()
  console.log('hackDevice', 'send', code)

  try {
    port.write(code)
    port.write("\n")
  } catch (e) {
  }
}

queue_process()

function send(code) {
  command_queue.push(code)
}

module.exports = {
  processor,
  send
}