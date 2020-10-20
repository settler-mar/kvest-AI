<template>
  <tr :id="'scales_'+item.id">
    <td>
      {{ item.date }}
    </td>
    <td>
      {{ item.time }}
    </td>
    <td>
      {{ item.type }}
    </td>
    <td>
      <num :item="item.value[0]" :code="'scales_'+item.id" start="0"/>
    </td>
    <td>
      <num v-if="item.value[1]" :item="item.value[1]" :code="'scales_'+item.id" :start="item.value[0].plate?1:2"/>
    </td>
    <td>
      {{ item.weight }}
    </td>
  </tr>
</template>

<script>
  import num from './numberBlock.vue'

  export default {
    data: function () {
      return {
      }
    },
    components: {
      num
    },
    props:[
      'item'
    ],
    computed: {
    },
    mounted:function(){
      //console.log(this.item)
    }
  }
</script>
