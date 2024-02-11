<template>
  <a-config-provider
    :locale="zhCN"
    :getPopupContainer="getPopupContainer"
    :theme="themeComputed"
  >
    <a-app>
      <router-view />
    </a-app>
  </a-config-provider>
</template>

<script lang="tsx" setup>
import {
  watch,
  computed,
  onMounted,
  getCurrentInstance,
  ComponentInternalInstance,
} from "vue";
import zhCN from "ant-design-vue/es/locale/zh_CN";
import { theme } from "ant-design-vue";

const currentInstance = getCurrentInstance() as ComponentInternalInstance;
const global = currentInstance.appContext.config.globalProperties;

const currentMobileMode = computed(() => {
  return global.$store.state.app.currentMobileMode;
}) as any;

const themeComputed = computed(() => {
  return {
    algorithm: systemSettings.value.darkMode ? theme.darkAlgorithm : undefined,
  };
}) as any;

const systemSettings = computed(() => global.$store.state.app.systemSettings);

watch(
  () => currentMobileMode.value,
  () => {
    initRemResizing();
  }
);

const initRemResizing = () => {
  let fontSize = 20;
  if (global.$store.state.app.currentMobileMode) {
    fontSize = 30;
  }

  global.$remResizing({
    baseline: 320,
    fontSize: fontSize,
    threshold: 640,
  });
};
const getPopupContainer = (el: any, dialogContext: any) => {
  if (dialogContext) {
    return dialogContext.getDialogWrap();
  } else {
    return document.body;
  }
};

onMounted(() => {
  initRemResizing();
});
</script>

<style scoped lang="scss">
.gallery_container {
  background: #ccc;
  .header {
    height: 10rem;
    font-size: 0.7rem;
  }
}

nav {
  padding: 30px;

  a {
    font-weight: bold;
    color: #2c3e50;

    &.router-link-exact-active {
      color: #42b983;
    }
  }
}
</style>
