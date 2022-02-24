const sassMiddleware = require('node-sass-middleware');
const path = require("path");

module.exports.init = (app, config) => {
  app.use(sassMiddleware({
    /* Options */
    src: path.join(config.source, 'scss'),
    dest: path.join(config.static, 'css'),
    debug: false,
    response: true,
    //outputStyle: 'compressed',
    force: true,
    outputStyle: 'extended',
    prefix: '/css'  // Where prefix is at <link rel="stylesheets" href="prefix/style.css"/>
  }));
}
