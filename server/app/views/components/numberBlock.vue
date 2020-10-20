<template>
  <div class="car-wrap">
    <div v-if="item.plate">
      {{item.plate}}<br>
      <img :src="imgCarNum" class="carNumber" :alt="item.plate" @click="show(0)">
    </div>
    <img :src="imgCar" class="car_full" @click="show(1)">
  </div>
</template>

<script>
  export default {
    data: function () {
      return {
        viewer: false
      }
    },
    props:[
      'item',
      'code',
      'start',
    ],
    computed: {
      imgCarNum (){
        return this.item.src + "_n."+this.item.imgFormat;
      },
      imgCar (){
        return this.item.src + "."+this.item.imgFormat;
      }
    },
    methods: {
      show (code) {
        if(!this.viewer) {
          var vue = this
          this.viewer = new Viewer(document.getElementById(this.code), {
            toolbar: {
              zoomIn: 4,
              zoomOut: 4,
              oneToOne: 4,
              reset: 0,
              prev: 4,
              play: {
                show: 4,
                size: 'large',
              },
              next: 4,
              rotateLeft: 0,
              rotateRight: 0,
              flipHorizontal: 0,
              flipVertical: 0,
            },
            movable: false,
            rotatable: false,
            hidden(){
              this.classList.remove('active')
            },
            viewed() {
              this.classList.add('active')
            },
          }).show()
        }
      }
    }
  }
</script>
