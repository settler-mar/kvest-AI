<template>
  <div>
    {{value}}
  </div>
</template>

<script>
  export default {
    data: function () {
      return {
      }
    },
    props:['params','data'],
    computed: {
      value(){
        return this.params.list[this.data]||'';
      }
    },
    mounted:function(){
      //console.log(this.item)
    }
  }
</script>
