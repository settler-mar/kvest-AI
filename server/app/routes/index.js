'use strict';

module.exports = (router, config) => {
  router.get("/",
    (req, res) => {
      var d = new Date();
      const data = {
        title: config.appName||"Квест <<Искусственный интеллект>>",
        year: d.getFullYear(),
        month: d.getMonth(),
        esp_list: esp_name,
        game_list: esp_list,
        game: game,
        status:esp_status,
      };
      let meta = {
        head: {
          title: config.name||'Test',
          metas: [
            { property:'og:title', content: config.name||'Test'},
            { name:'twitter:title', content: config.name||'Test'},
          ],
        }
      };
      //res.send(req.vueOptions);
      res.renderVue("main.vue", data, meta);
    },
  );
};