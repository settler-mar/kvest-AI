//@ts-check
const path = require("path");

class Config {
    constructor() {
        this.env = process.env.NODE_ENV || "production";
        this.static = path.normalize(__dirname + "/../../public");
        this.source = path.normalize(__dirname + "/../../source");
        this.root = path.normalize(__dirname + "/..");
        this.rootPath = process.env.ROOT_PATH || "/";
        this.app = {
            name: "Express-Vue-MVC-Starter",
        };
        this.port = Number(process.env.PORT) || 8080;
    }
}
module.exports = Config;
