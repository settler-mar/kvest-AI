<template>
  <div>
    {{data}}
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
    },
    mounted:function(){
      //console.log(this.item)
    }
  }
</script>
