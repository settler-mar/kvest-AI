<template>
  <div>
    <span class="el_gloves" v-for="code in imgs" :data-code="code" :data-room="room(code)">
      <img :src="get_src(code)"/>
    </span>
  </div>
</template>

<script>
export default {
  data: function () {
    return {}
  },
  props: ['params', 'data'],
  computed: {
    imgs() {
      if (!this.data) return []
      return this.data.trim().replace(/\_+$/g, '').split('_')
    }
  },
  methods: {
    room(id) {
      if (id > 9) return 1
      return 0
    },
    get_src(id) {
      id = id * 1
      if (id > 9) {
        id -= 2
      }
      id += 1
      return '/img/symbols32x32/_' + id + '.png'
    }
  },
  mounted: function () {
  }
}
</script>
