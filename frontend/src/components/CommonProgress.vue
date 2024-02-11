<template>
  <div class="common_progress_item">
    <p>{{ Math.floor(progress) }}</p>
    <span :style="progressStyle"></span>
  </div>
</template>

<script lang="ts">
import { defineComponent } from "vue";

export default defineComponent({
  name: "CommonProgress",
  props: {
    progress: {
      type: Number,
      default: 100,
    },
  },
  computed: {
    progressStyle() {
      let result: any = isNaN(Number(this.progress)) ? 0 : this.progress;
      return {
        width: result + "%",
      };
    },
  },
});
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped lang="scss">
.common_progress_item {
  height: 0.1rem;
  width: 100%;
  p {
    display: block;
    font-size: 0.65rem;
    color: #999;
  }
  span {
    display: block;
    height: 100%;
    background-color: #999;
    transition: all 0.5s;
  }
}
</style>
