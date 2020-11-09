<template>
  <div class="progress_wrap">
    {{value}}/{{max}}
    <div class="progress_box">
      <span class="progress_el" :style="style"></span>
    </div>
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
        var v = this.data-this.params.min
        if (v>this.params.max){
          v=this.params.max
        }
        if (v<0){
          v=0
        }
        return v?v:0;
      },
      max(){
        return this.params.max-this.params.min
      },
      style(){
        return 'width:'+(100*this.value/this.max)+'%'
      }
    },
    mounted:function(){
      //console.log(this.item)
    }
  }
</script>
