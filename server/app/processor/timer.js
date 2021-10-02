const http = require('http');

module.exports = function (code) {
  http.request({host: '127.0.0.1', 'port': 8083, 'path': code}).on('error', (e) => {
    //console.error(`problem with request: ${e.message}`);
  }).end();
}