<template>
  <div :class="value"></div>
</template>

<script>
  //status_true
  //status_false
  //
  export default {
    data: function () {
      return {}
    },
    props: ['params', 'data'],
    computed: {
      value(){
        if (this.data == NaN) {
          return ''
        }
        return 'el_status el_status_' + this.data
        //return typeof (this.data||'');
      }
    },
    mounted: function () {
      //console.log(this.item)
    }
  }
</script>
