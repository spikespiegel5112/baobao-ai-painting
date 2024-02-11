<template>
  <div class="img2img_container" ref="img2imgContainerRef">
    <div class="main">
      <div class="common_tab_container">
        <div class="mask"></div>
        <ul class="tabnav">
          <li v-for="item in state.tabList" :class="{ active: state.activeTab === item.name }">
            <a href="javascript:;" @click="handleChooseTab(item)">{{ item.title }}</a>
          </li>
        </ul>
        <div class="tabpane">
          <div v-html="state.tabList.find((item: any) => item.name === state.activeTab).component"></div>
        </div>

      </div>
      <!-- <a-tabs v-model:active-key="state.activeTab">
            <a-tab-pane key="inpaint" tab="inpaint">重绘</a-tab-pane>
            <a-tab-pane key="reimagine" tab="reimagine">联想</a-tab-pane>
          </a-tabs> -->
    </div>
  </div>
</template>

<script lang="tsx" setup>
import {
  reactive,
  watch,
  computed,
  onMounted,
  onBeforeUnmount,
  getCurrentInstance,
  ComponentInternalInstance,
  ref,
  nextTick,
} from "vue";

import Inpaint from './Inpaint.vue'


const currentInstance = getCurrentInstance() as ComponentInternalInstance;
const global = currentInstance.appContext.config.globalProperties;

const loading = ref(true);

// const loadingInstance = ElLoading.service();
const state = reactive({
  activeTab: 'inpaint',
  tabList: [{
    title: '重绘',
    name: 'inpaint',
    component: 'Impaint'
  }, {
    title: '联想',
    name: 'reimagine',
    component: 'Reimagine'
  }]
});

watch(
  () => global.$router.currentRoute.value,
  (newValue: any, oldValue: any) => { }
);

const initCachedPreviewData = () => {
  const txt2ImgSessionData = global.$getTxt2ImgSessionData();
  global.$store.commit("app/updateCurrentPreviewList", txt2ImgSessionData);
  state.readyFlag = true;
};

const handlePositivePromptChanged = (data: any) => {
  state.positivePrompt = data.options;
  state.customPositivePrompt = data.custom;
};

const handleNegativePromptChanged = (data: any) => {
  state.negativePrompt = data.options;
  state.customNegativePrompt = data.custom;
};

const handleSettingChanged = (data: any) => {
  state.settings = data;
  state.useNegativePrompt = data.useNegativePrompt;
  state.setSeed = data.setSeed;
  state.useRefiner = data.useRefiner;
  state.useFp32 = data.useFp32;
  state.useLcmLora = data.useLcmLora;
  state.sampler = data.sampler;
};

const handleIsUsingNegativeChanged = (value: boolean) => {
  state.useNegativePrompt = value;
};

const handleChoosePreview = (index: number) => {
  state.chosenPreviewIndex = index;
};

const handleApplySeed = (seed: number | null) => {
  state.appliedSeed = seed;
};

const handleChooseTab = (item: any) => {
  state.activeTab = item.name

}

onMounted(async () => {
  global.$NProgress.done();



});

onBeforeUnmount(() => {
  // state.onProgress = false;
});
</script>

<style lang="scss">
.img2img_container {
  height: 100vh;


  .main {
    margin: 1.5rem 0 0 0;
    height: calc(100% - 1.5rem);

  }
}

.common_tab_container {
  width: 100%;
  height: 100%;
  position: relative;

  .mask {
    backdrop-filter: blur(5px);
  }

  .tabnav {
    width: 100%;
    background-color: rgba($color: #fff, $alpha: 0.15);
    border: 0;
    position: absolute;
    top: 0;
    left: 0;
    text-align: center;
    border: 0;

    li {
      display: inline-block;
      min-width: 1.5rem;
      height: 0.8rem;
      line-height: 0.8rem;
      vertical-align: middle;

      &.active {
        a {
          background-color: #aaa;
          color: #000;

          &:hover {
            background-color: #aaa;
            color: #000;
          }
        }

      }

      a {
        display: inline-block;
        padding: 0;
        width: 100%;
        height: 100%;
        color: #fff;
        text-align: center;
        transition: all 0.3s;

        &:hover {
          background-color: #333;
          color: #fff;
        }
      }
    }
  }

  .tabpane {
    height: 100%;
  }
}
</style>
