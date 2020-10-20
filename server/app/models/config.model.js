//@ts-check
const path = require("path");

class Config {
    constructor() {
        this.env = process.env.NODE_ENV || "development";
        this.static = path.normalize(__dirname + "/../../public");
        this.source = path.normalize(__dirname + "/../../source");
        this.root = path.normalize(__dirname + "/..");
        this.rootPath = process.env.ROOT_PATH || "/";
        this.app = {
            name: "Express-Vue-MVC-Starter",
        };
        this.port = Number(process.env.PORT) || 9000;
        this.wss_port = Number(process.env.PORT_WSS) || 8080;
    }
}
module.exports = Config;
