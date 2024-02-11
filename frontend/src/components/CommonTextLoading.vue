<template>
  <div class="loader-inner ball-pulse">
    <div></div>
    <div></div>
    <div></div>
  </div>
</template>

<script lang="ts">
import { defineComponent } from "vue";

export default defineComponent({
  name: "CommonTextLoading",
  props: {
    msg: String,
  },
});
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped lang="scss">
.ball-pulse > div:nth-child(0) {
  -webkit-animation: scale 0.75s 0s infinite cubic-bezier(0.2, 0.68, 0.18, 1.08);
  animation: scale 0.75s 0s infinite cubic-bezier(0.2, 0.68, 0.18, 1.08);
}

.ball-pulse > div:nth-child(1) {
  -webkit-animation: scale 0.75s 0.12s infinite
    cubic-bezier(0.2, 0.68, 0.18, 1.08);
  animation: scale 0.75s 0.12s infinite cubic-bezier(0.2, 0.68, 0.18, 1.08);
}

.ball-pulse > div:nth-child(2) {
  -webkit-animation: scale 0.75s 0.24s infinite
    cubic-bezier(0.2, 0.68, 0.18, 1.08);
  animation: scale 0.75s 0.24s infinite cubic-bezier(0.2, 0.68, 0.18, 1.08);
}

.ball-pulse > div:nth-child(3) {
  -webkit-animation: scale 0.75s 0.36s infinite
    cubic-bezier(0.2, 0.68, 0.18, 1.08);
  animation: scale 0.75s 0.36s infinite cubic-bezier(0.2, 0.68, 0.18, 1.08);
}

.ball-pulse > div {
  background-color: #000;
  width: 0.3rem;
  height: 0.3rem;
  border-radius: 100%;
  margin: 2px;
  -webkit-animation-fill-mode: both;
  animation-fill-mode: both;
  display: inline-block;
}

@-webkit-keyframes ball-pulse-sync {
  33% {
    -webkit-transform: translateY(10px);
    transform: translateY(10px);
  }

  66% {
    -webkit-transform: translateY(-10px);
    transform: translateY(-10px);
  }

  100% {
    -webkit-transform: translateY(0);
    transform: translateY(0);
  }
}

@keyframes ball-pulse-sync {
  33% {
    -webkit-transform: translateY(10px);
    transform: translateY(10px);
  }

  66% {
    -webkit-transform: translateY(-10px);
    transform: translateY(-10px);
  }

  100% {
    -webkit-transform: translateY(0);
    transform: translateY(0);
  }
}

@keyframes scale {
  30% {
    -webkit-transform: scale(0.3);
    transform: scale(0.3);
  }

  100% {
    -webkit-transform: scale(1);
    transform: scale(1);
  }
}

.ball-pulse-sync > div:nth-child(0) {
  -webkit-animation: ball-pulse-sync 0.6s 0s infinite ease-in-out;
  animation: ball-pulse-sync 0.6s 0s infinite ease-in-out;
}

.ball-pulse-sync > div:nth-child(1) {
  -webkit-animation: ball-pulse-sync 0.6s 0.07s infinite ease-in-out;
  animation: ball-pulse-sync 0.6s 0.07s infinite ease-in-out;
}

.ball-pulse-sync > div:nth-child(2) {
  -webkit-animation: ball-pulse-sync 0.6s 0.14s infinite ease-in-out;
  animation: ball-pulse-sync 0.6s 0.14s infinite ease-in-out;
}

.ball-pulse-sync > div:nth-child(3) {
  -webkit-animation: ball-pulse-sync 0.6s 0.21s infinite ease-in-out;
  animation: ball-pulse-sync 0.6s 0.21s infinite ease-in-out;
}

.ball-pulse-sync > div {
  background-color: #000;
  width: 15px;
  height: 15px;
  border-radius: 100%;
  margin: 2px;
  -webkit-animation-fill-mode: both;
  animation-fill-mode: both;
  display: inline-block;
}
</style>
