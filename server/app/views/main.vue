<template xmlns="http://www.w3.org/1999/html">
  <div class="main-wrap">
    <header>
      <h1>{{title}}</h1>
    </header>
    <nav>
      <span>Текущая игра: {{game.timer}}</span>
      <span>
        <button v-on:click="evReset" v-if="game.status==0">Сброс</button>
        <button v-on:click="evStart" v-if="game.status==0">Старт</button>
        <button v-on:click="evStop"  v-if="game.status==1 || game.status==2">Стоп</button>
        <button v-on:click="evStart" v-if="game.status==2">Продолжить</button>
        <button v-on:click="evPause" v-if="game.status==1">Пауза</button>
      </span>
      <span>{{time}}</span>
    </nav>
    <section class="main">
      <table class="esp_status">
        <thead>
          <tr>
            <th>CODE</th>
            <th>API</th>
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
          <th>Дата</th>
          <th>Время</th>
          <th>Метод</th>
          <th># машины(спереди)</th>
          <th># машины(сзади)</th>
          <th>вес</th>
        </tr>
        </thead>
        <tbody v-if="loading">
        <tr>
          <td colspan="6">
            Обновление данных...
          </td>
        </tr>
        </tbody>
        <tbody v-else>
        <tr v-if="noRecord">
          <td colspan="6">Записей не найдено((</td>
        </tr>
        <table-line v-for="item in items" :item="item"></table-line>
        </tbody>
      </table>
    </section>
    <footer>
      Система управления квест комнатой
    </footer>
  </div>
</template>

<script>
  import TableLine from './components/TableLine.vue'

  export default {
    data: function () {
      return {
        showCount: 20,
        countLoaded: 20,
        showPage: 1,
        collection: [],
        time: '-',
        weight: '-',
        months: ['январь', 'февраль', 'март', 'апрель', 'май', 'июнь', 'июль', 'август', 'сентябрь', 'октябрь', 'ноябрь', 'декабрь'],
        loading: false,
        db:[],
      }
    },
    components: {
      TableLine
    },
    methods: {
      get(list,key,name){
        if(!(key in list)) return ""
        if(!(name in list[key])) return ""
        return list[key][name]
      },
      evStart(e){
        ws.send('Start')
      },
      evReset(e){
        ws.send('Reset')
      },
      evStop(e){
        ws.send('Stop')
      },
      evPause(e){
        ws.send('Pause')
      },
    },
    mounted() {
      //fetch('data')
    },
    asyncComputed: {},
    computed: {
      esp_table(){
        var out = []
        for(var code in this.esp_list){
          var item = this.esp_list[code]
          out.push({
            code,
            ip:item?item.ip:'',
            online:item?item.online:false,
          })
        }
        return out
      },
      totalItem() {
        if (!this.db[this.year]) return '-';
        if (!this.db[this.year][this.month]) return '-';
        return this.db[this.year][this.month].length;
      },
      items() {
        this.loading = true
        var vue = this;
        if (!this.year) return [];
        if (!this.db[this.year]) {
          this.db[this.year] = {};
        }
        if (!this.db[this.year][this.month]) {
          if (typeof (getDataDb) == 'function') {
            const url = '/get/' + this.year + '/' + this.month;
            var b = getDataDb(url)
          }
          return []
        }
        let data = getList()
        this.loading = false
        return data;
      },
      years() {
        const year = new Date().getFullYear() + 1
        return Array.from({length: year - 2019}, (value, index) => 2019 + index)
      },
      noRecord() {
        if (!this.db[this.year]) return true;
        if (!this.db[this.year][this.month]) return true;
        return this.db[this.year][this.month].length == 0;
      },
      maxPage() {
        if (!this.db[this.year]) return 0;
        if (!this.db[this.year][this.month]) return 0;
        return Math.ceil(this.db[this.year][this.month].length / this.showCount)
      }
    },
  }
</script>
