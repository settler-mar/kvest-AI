<template xmlns="http://www.w3.org/1999/html">
  <div class="main-wrap">
    <header>
      <h1>{{title}}</h1>
    </header>
    <nav>
      <span>Текущая игра: {{game.timer}}</span>
      <span>
        <button v-on:click="evReset" v-if="game.status==0 || game.status==-1">Сброс</button>
        <button v-on:click="evStart" v-if="game.status==0">Старт</button>
        <button v-on:click="evStop" v-if="game.status==1 || game.status==2">Стоп</button>
        <button v-on:click="evStart" v-if="game.status==2">Продолжить</button>
        <button v-on:click="evPause" v-if="game.status==1">Пауза</button>
        <button v-on:click="evAddTime" v-if="game.status==1 || game.status==2">+5min</button>
      </span>
      <div>
        Язык игры
        <select v-on:change="setLang" v-model="game.lang">
          <option value="ru">Рус</option>
          <option value="ua">Укр</option>
          <option value="en">Англ</option>
        </select>
      </div>

      <div>
        Активная игры
        <select v-model="game.device_game" v-on:change="setGame">
          <option value="1">Вентиляция</option>
          <option value="2">Взлом двери</option>
          <option value="3">Перчатки</option>
        </select>
      </div>
      <span>{{time}}</span>
    </nav>
    <section class="main">
      <table class="esp_status">
        <thead>
        <tr>
          <th>CODE</th>
          <th>IP</th>
          <th>STATUS</th>
        </tr>
        </thead>
        <tr v-for="item in esp_table">
          <td>{{item.code}}</td>
          <td>{{item.ip}}</td>
          <td>{{item.online?'+':'-'}}</td>
        </tr>
      </table>
      <table>
        <thead>
        <tr>
          <th>Этап</th>
          <th>Параметр</th>
          <th>Состояние</th>
          <th>Действие</th>
        </tr>
        </thead>
        <tbody>
        <template v-for="(item,i) in game_list" v-if="item.display!==false">
          <tr class="device_line">
            <td :rowspan="Object.keys(item.status).length + 1">{{item.name}}</td>
            <td colspan="2" style="padding: 0;"></td>
            <td :rowspan="Object.keys(item.status).length + 1">
              <div v-for="(title, com) in item.commands">
                <button v-on:click="evCommand(item.code,com)">{{title}}</button>
              </div>
            </td>
          </tr>
          <tr v-for="(st,code) in item.status">
            <td>{{st.title}}</td>
            <td>
              <el_list v-if="st.type=='list'" :params="st" :data="get_status(item.code,code)"/>
              <el_text v-if="st.type=='text'" :params="st" :data="get_status(item.code,code)"/>
              <el_progress v-else-if="st.type=='progress'" :params="st" :data="get_status(item.code,code)"/>
              <el_status v-else-if="st.type=='status'" :params="st" :data="get_status(item.code,code)"/>
              <el_gloves v-else-if="st.type=='gloves'" :params="st" :data="get_status(item.code,code)"/>

            </td>
          </tr>
        </template>
        </tbody>
      </table>
    </section>
    <footer>
      Система управления квест комнатой
    </footer>
  </div>
</template>

<script>
  import el_list from './components/el_list.vue'
  import el_progress from './components/el_progress.vue'
  import el_status from './components/el_status.vue'
  import el_text from './components/el_text.vue'
  import el_gloves from './components/el_gloves.vue'

  export default {
    data: function () {
      return {
        time: '-',
        weight: '-',
        months: ['январь', 'февраль', 'март', 'апрель', 'май', 'июнь', 'июль', 'август', 'сентябрь', 'октябрь', 'ноябрь', 'декабрь'],
        loading: false,
        db: [],
      }
    },
    components: {
      el_list, el_progress, el_status, el_text, el_gloves
    },
    methods: {
      evStart(e){
        ws.send('start')
      },
      evReset(e){
        ws.send('reset')
      },
      evStop(e){
        ws.send('stop')
      },
      evPause(e){
        ws.send('pause')
      },
      evAddTime(e){
        ws.send('addTime')
      },
      evCommand(name, command){
        console.log([name, command].join(':'))
        ws.send([name, command].join(':'))
      },
      get_status(el, code){
        if (this.status[el] && this.status[el][code]) {
          return this.status[el][code]
        }
        return NaN
      },
      setLang(e){
        ws.send(["lang", e.srcElement.value].join(':'))
      },
      setGame(e){
        ws.send(["game", e.srcElement.value].join(':'))
      }

    },
    mounted() {
      //fetch('data')
    },
    asyncComputed: {},
    computed: {
      esp_table(){
        var out = []
        for (var code in this.esp_list) {
          var item = this.esp_list[code]
          out.push({
            code,
            ip: item ? item.ip : '',
            online: item ? item.online : false,
          })
        }
        return out
      }
    },
  }
</script>
