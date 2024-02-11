<template>
  <el-dialog
    class="previewpromptdialog_container"
    top="0"
    close-on-press-escape
    destroy-on-close
    :show-close="false"
    v-model="state.innerPreviewPromptVisible"
  >
    <div class="content">
      <el-button class="close" icon="Close" link @click="handleCloseDialog">
      </el-button>
      <el-scrollbar>
        <div class="prompt_wrapper custompositiveprompt">
          <h5>自定义提示词</h5>
          <p v-if="global.$isNotEmpty(props.customPositivePrompt.trim())">
            {{ props.customPositivePrompt }}
          </p>
          <p class="empty" v-else>无</p>
        </div>
        <div
          class="prompt_wrapper positiveprompt"
          v-if="positivePromptList.length > 0"
        >
          <a-row class="header">
            <a-col class="left" :span="12">
              <h5>选项提示词</h5>
            </a-col>
            <a-col class="right" :span="12">
              <span>显示实际提示词</span>
              <el-switch
                v-model="state.switchPositivePromptDisplay"
              ></el-switch>
            </a-col>
          </a-row>
          <ul>
            <li
              v-for="(item, index) in positivePromptList"
              :key="index"
              :style="item.style"
            >
              {{ state.switchPositivePromptDisplay ? item.value : item.title }}
              <span
                v-if="
                  state.switchPositivePromptDisplay &&
                  index < positivePromptList.length - 1
                "
              >
                ,
              </span>
            </li>
          </ul>
        </div>
        <div
          class="prompt_wrapper customnegativeprompt"
          v-if="
            global.$isNotEmpty(props.customNegativePrompt.trim()) &&
            props.useNegativePrompt
          "
        >
          <h5>反向自定义提示词</h5>
          <p>
            {{ props.customNegativePrompt }}
          </p>
        </div>
        <div
          class="prompt_wrapper negativeprompt"
          v-if="negativePromptList.length > 0 && props.useNegativePrompt"
        >
          <a-row class="header">
            <a-col class="left" :span="12">
              <h5>反向选项提示词</h5>
            </a-col>
            <a-col class="right" :span="12">
              <span>显示实际提示词</span>
              <el-switch
                v-model="state.switchNegativePromptDisplay"
              ></el-switch>
            </a-col>
          </a-row>
          <ul>
            <li
              v-for="(item, index) in negativePromptList"
              :key="index"
              :style="item.style"
            >
              {{ state.switchNegativePromptDisplay ? item.value : item.title }}
              <span
                v-if="
                  state.switchNegativePromptDisplay &&
                  index < negativePromptList.length - 1
                "
              >
                ,
              </span>
            </li>
          </ul>
        </div>
      </el-scrollbar>
      <div class="aside">
        <ul>
          <li>
            <span>宽度：</span>
            <p>{{ props.width }}</p>
          </li>
          <li>
            <span>高度：</span>
            <p>{{ props.height }}</p>
          </li>
          <li v-if="props.setSeed">
            <span>种子：</span>
            <p>{{ props.seed }}</p>
          </li>
          <li>
            <span>步数：</span>
            <p>{{ props.numInferenceSteps }}</p>
          </li>
          <li v-if="props.useRefiner">
            <span>Refiner步数：</span>
            <p>{{ props.numInferenceStepsRefiner }}</p>
          </li>
        </ul>
      </div>
    </div>
  </el-dialog>
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
} from "vue";

const currentInstance = getCurrentInstance() as ComponentInternalInstance;
const global = currentInstance.appContext.config.globalProperties;

interface Props {
  previewPromptVisible?: boolean;
  positivePromptList?: string[];
  customPositivePrompt?: string;
  negativePromptList: string[];
  customNegativePrompt?: string;
  useNegativePrompt: boolean;
  useRefiner: boolean;
  width: number;
  height: number;
  seed: number | null;
  setSeed: boolean;
  numInferenceSteps: number;
  numInferenceStepsRefiner: number;
}

const props = withDefaults(defineProps<Props>(), {
  previewPromptVisible: false,
  positivePromptList: [] as any,
  customPositivePrompt: "",
  negativePromptList: [] as any,
  customNegativePrompt: "",
  useNegativePrompt: false,
  useRefiner: false,
  width: 0,
  height: 0,
  seed: null,
  setSeed: false,
  numInferenceSteps: 0,
  numInferenceStepsRefiner: 0,
});

const emit = defineEmits<{
  (e: "onCloseDialog", data: any): void;
}>();

// const loadingInstance = ElLoading.service();
const state = reactive({
  switchPositivePromptDisplay: false,
  switchNegativePromptDisplay: false,
  innerPreviewPromptVisible: false,
});

const positivePromptList = computed(() => {
  let result = [] as any;
  if (!props.positivePromptList) return result;

  props.positivePromptList.forEach((item: any) => {
    result.push(...item.content.filter((item2: any) => item2.active));
  });
  const length = result.length;
  let randomData = global.$generateRandom(length);
  const interval = 1.5 / randomData.length;
  result = result.map((item: any, index: number) => {
    return {
      ...item,
      style: {
        "animation-delay": randomData[index] * interval + "s",
        "animation-name": "fadeIn",
        "animation-duration": "1s",
        "animation-fill-mode": "forwards",
      },
    };
  });

  return result;
}) as any;

const negativePromptList = computed(() => {
  let result = [] as any;
  if (!props.negativePromptList) return result;
  props.negativePromptList.forEach((item: any) => {
    result.push(...item.content.filter((item2: any) => item2.active));
  });

  const length = result.length;
  let randomData = global.$generateRandom(length);
  const interval = 1.5 / randomData.length;
  result = result.map((item: any, index: number) => {
    return {
      ...item,
      style: {
        "animation-delay": randomData[index] * interval + "s",
        "animation-name": "fadeIn",
        "animation-duration": "1s",
        "animation-fill-mode": "forwards",
      },
    };
  });
  return result;
}) as any;

watch(
  () => global.$router.currentRoute.value,
  (newValue: any, oldValue: any) => {}
);

watch(
  () => props.previewPromptVisible,
  (newValue: any, oldValue: any) => {
    state.innerPreviewPromptVisible = newValue;
  }
);

const handleCloseDialog = () => {
  emit("onCloseDialog", false);
};

const positivePromptRandomAnimation = () => {
  const length = positivePromptList.value.length;
  const randomData: number[] = global.$generateRandom(length);
  positivePromptList.value.forEach((item: any, index: number) => {
    item = {
      ...item,
      randomIndex: randomData[index],
    };
  });
};

const otherSettingsObject = () => {
  const otherSettingsString: string = props.otherSettings;
  if (!otherSettingsString) return;
  const result = JSON.parse(otherSettingsString);
  return result;
};

const parseOtherSettings = () => {
  parseOtherSettings;
};

onMounted(async () => {
  positivePromptRandomAnimation();
  parseOtherSettings();
});

onBeforeUnmount(() => {});
</script>

<style lang="scss">
.previewpromptdialog_container {
  display: flex;
  width: 100%;
  height: 100vh;
  flex-direction: column;
  color: #ccc;
  position: relative;
  box-sizing: border-box;
  position: fixed;
  overflow: hidden;

  background-color: rgba($color: #000000, $alpha: 0.5);
  backdrop-filter: blur(5px);
  .close {
    position: absolute;
    right: -4rem;
    top: 0rem;
    font-size: 1.8rem;
  }
  .content {
    margin: 0 auto;
    width: 15rem;
    position: relative;
    h5 {
      padding: 0 0 0.1rem 0;
      width: 15rem;
      font-size: 0.6rem;
      color: #fff;
      border-bottom: 1px solid #ccc;
    }
    .el-scrollbar {
      height: 90vh;
      .empty {
        font-size: 0.6rem;
        color: #fff;
        font-style: italic;
      }

      .prompt_wrapper {
        .header {
          .right {
            color: #fff;
            text-align: right;
            > span {
              display: inline-block;
              margin: 0 0.2rem 0 0;
              vertical-align: middle;
            }
          }
        }
        p {
          margin: 0.3rem 0 1rem 0;
          word-wrap: break-word;
        }
        ul {
          margin: 0.3rem 0 1rem 0;
          li {
            display: inline-block;
            margin: 0.3rem 0.2rem 0 0;
            font-size: 0.5rem;
            font-style: italic;
            color: #fff;
            opacity: 0;
          }
        }
        .empty {
          margin: 0.5rem 0 1rem 0;
          font-size: 0.6rem;
        }
      }
      .custompositiveprompt {
        font-size: 0.9rem;
        p {
          color: #fff;
        }
      }
      .customnegativeprompt {
        font-size: 0.6rem;
        p {
          color: #fff;
        }
      }
    }
    .aside {
      position: absolute;
      top: 4rem;
      left: 16rem;
      ul {
        li {
          width: 6rem;
          font-size: 0.5rem;
          color: #fff;
          span {
            display: inline-block;
            width: 4rem;
          }
          p {
            display: inline-block;
            width: 1rem;
            text-align: right;
          }
        }
      }
    }
  }
  @keyframes fadeIn {
    0% {
      opacity: 0;
    }
    100% {
      opacity: 1;
    }
  }
}
</style>
