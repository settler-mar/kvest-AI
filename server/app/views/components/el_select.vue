<template>
  <select v-model="value">
    <option :value="i" v-for="i in params.list">{{ i }}</option>
  </select>
</template>

<script>
export default {
  data: function () {
    return {}
  },
  props: ['params', 'data', 'code', 'name'],
  computed: {
    value: {
      get() {
        return this.data;
      }, set(val) {
        ws.send([this.name, this.code + val].join(':'))
      }
    }
  },
  mounted: function () {
    //console.log(this.item)
  }
}
</script>
