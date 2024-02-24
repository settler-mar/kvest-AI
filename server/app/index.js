//@ts-check
const express = require("express");
const http = require('http');
const requestIp = require('request-ip');

const config = require("./modules/config");
const Router = require("./modules/router");
const Style = require("./modules/style");
const wss = require("./modules/wss");
const game = require("./modules/game");
const external_proc = require("./modules/external_proc");

let app = express();
let web = http.createServer(app);

Style.init(app, config);
app.use(requestIp.mw())
Router.init(app, config);
wss.init(web, config);

game(config);

const port = config.port || 8080;

setTimeout(external_proc, 5000)
web.listen(port, '0.0.0.0', (err) => {
  console.log(`Worker ${process.pid} running a ${config.env} server. Запущен веб интерфейс по адресу http://0.0.0.0:${port}`)
});



