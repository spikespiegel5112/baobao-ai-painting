<template>
  <div class="useravatar_item">
    <img v-if="!!userAvatar" :src="userAvatar" alt="" />
    <HaitongUnitrustHorseAvatar v-else />
  </div>
</template>

<script lang="tsx" setup>
import { computed, getCurrentInstance, ComponentInternalInstance } from "vue";

const currentInstance = getCurrentInstance() as ComponentInternalInstance;
const global = currentInstance.appContext.config.globalProperties;

const userAvatar = computed(() => {
  const userInfo = global.$store.state.user.userInfo;
  const result = global.$isNotEmpty(userInfo)
    ? userInfo.avatar
    : null;
  return result;
}) as any;
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped lang="scss">
.useravatar_item {
  width: 1rem;
  height: 1rem;
  img {
    display: inline-block;
    width: 100%;
    height: 100%;
  }
}
</style>
