//@ts-check
const express = require("express");
const glob = require("glob");
const logger = require("morgan");
const cookieParser = require("cookie-parser");
const bodyParser = require("body-parser");
const compress = require("compression");
const methodOverride = require("method-override");
const cookieSession = require("cookie-session");
const helmet = require("helmet");
const validator = require("express-validator");
const expressVue = require("express-vue");
const path = require("path");
const favicon = require('serve-favicon');
const cors = require('cors');

/**
 *
 * @param {object} app
 * @param {object} config
 */
module.exports.init = (app, config) => {
  //Setup
  const env = process.env.NODE_ENV || "development";
  const router = express.Router();
  let logType = "dev";
  app.locals.ENV = env;
  app.locals.ENV_DEVELOPMENT = (env === "development");

  //ExpressVue Setup
  const vueOptions = {
    pagesPath: path.join(config.root, "views"),
    rootPath: path.join(config.root, "views"),
    head: {
      styles: [{style: "css/index.css"}],
      scripts: [
        {src: "/js/run.js",},
      ]
    },
    //template: {
      html: {
        start: '<!DOCTYPE html><html>',
        end: '</html>'
      },
      body: {
        start: '<body>',
        end: '</body>'
      },
      template: {
        start: '<div id="apps">',
        end: '</div>'
      }
    //}
  };

  // @ts-ignore
  const expressVueMiddleware = expressVue.init(vueOptions)
  app.use(expressVueMiddleware);

  app.use(cors());

  //expressVue.use(app, vueOptions).then(() => {

    //Security
    app.use(helmet());
    app.disable("x-powered-by");

    app.use(bodyParser.json());
    app.use(bodyParser.urlencoded({
      extended: true,
    }));
    app.use(validator());

    app.use(compress());

    app.use(express.static(config.static));
    app.use(favicon(path.join(config.static, 'favicon.png')))

    let sessionConfig = {
      name: "session",
      keys: [
        "CHANGE_ME",
      ],
      resave: true,
      saveUninitialized: true,
      cookie: {
        domain: "foo.bar.com",
        secure: false,
        httpOnly: true,
      },
    };
    if (env === "production") {
      app.set("trust proxy", 1);
      sessionConfig.cookie.secure = true;
      logType = "combined";
    }

    if (env === "development") {
      app.use(logger(logType));
    }

    app.use(cookieParser());

    app.use(methodOverride());

    app.use(cookieSession(sessionConfig));

    app.use("/", router);

    let controllers = glob.sync(config.root + "/routes/*.js");
    controllers.forEach(function (controller) {
      module.require(controller)(router, config);
    });

    /**
     * Generic 404 handler
     * @param {object} req
     * @param {object} res
     */
    function error404handler(req, res) {
      const data = {
        title: "Error 404",
      };
      req.vueOptions = {
        head: {
          title: "Error 404",
        },
      };
      res.statusCode = 404;
      res.renderVue("error.vue", data, req.vueOptions);
    }

    app.use(error404handler);
  //})
}
