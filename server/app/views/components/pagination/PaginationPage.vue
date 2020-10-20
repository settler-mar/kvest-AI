<template>
  <div class="pagination-block" v-if="maxPage>1">
    <ul>
      <li
              v-for="item in pagesList"
              :class="item.disabled?'disabled':item.isDot?'dotes':item.active?'active':''"
              @click="setPage(item.page)"
      >
        {{ item.text }}
      </li>
    </ul>
  </div>
</template>
<script>

  export default {
    name: 'PaginationPage',
    props: [
      'maxPage',
      'value'
    ],
    methods: {
      setPage(value) {
        if(!value)return;
        if(value<0 || value>this.maxPage) return;
        this.value = value
        this.$emit('input', value);
      }
    },
    computed: {
      pagesList: function () {
        if (this.value>this.maxPage)this.value=this.maxPage
        var out = [{
          disabled: this.value == 1,
          text: '<<',
          page: this.value - 1
        }, {
          active: this.value == 1,
          text: 1,
          page: 1
        }];

        var start = this.value - 4;
        var end = this.value + 4;

        if (start<3) end++
        if (end>=this.maxPage-1)start--

        if (start < 2) end += 2 - start
        if (end > this.maxPage-1) start -= (end-this.maxPage)+1

        if (end >= this.maxPage) end = this.maxPage -1
        if (start < 2) start = 2

        if(start > 2){
          out.push({
            isDot: true
          })
        }
        for (;start<=end;start++){
          out.push({
            active: this.value == start,
            text: start,
            page: start
          })
        }

        if(end != this.maxPage-1){
          out.push({
            isDot: true
          })
        }

        out.push({
          active: this.value == this.maxPage,
          text: this.maxPage,
          page: this.maxPage
        })

        out.push({
          disabled: this.value == this.maxPage,
          text: '>>',
          page:  this.value + 1
        })
        return out
      }
    },
  }
</script>

<style lang="scss">
  .pagination-block {
    ul {
      list-style: none;
      display: flex;
      margin: 0;

      li {
        cursor: pointer;
        padding: 2px 10px;
        min-width: 24px;
        text-align: center;

        &:hover {
          color: #33f;
        }

        &.disabled{
          color: #686868;
          cursor: default;
        }

        &.active{
          box-shadow: 0 0 1px 1px #33f;
          color: #2b2b9f;
          background: #fff;
          cursor: default;
        }

        &.dotes{
          cursor: default;

          &:before{
            content: '...';
            color: #fff;
          }
        }
      }
    }
  }
</style>
