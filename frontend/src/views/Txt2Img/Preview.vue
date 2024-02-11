<template>
  <div class="preview_container">
    <el-scrollbar class="preview_wrapper" height="100%" ref="scrollbarRef">
      <a-row class="button_item">
        <a-col :span="24">
          <a-button-group v-if="!state.onCancelling && !state.onProgress && !state.onCoolingDown
            ">
            <a-button type="primary" :disabled="state.generatingDisable || state.beginToGenerateFlag"
              @click="handleSubmitMessageByDiffuser">
              生成
              <!-- {{ state.generatingDisable }} -->
              <!-- {{ state.beginToGenerateFlag }} -->
            </a-button>
          </a-button-group>

          <el-button-group v-else-if="state.progressInfo.isSameUser">
            <el-button v-if="(state.onProgress || state.beginToGenerateFlag) &&
              !state.onCancelling &&
              global.$isEmpty(state.progressInfo.generatingIndexBase) &&
              global.$isEmpty(state.progressInfo.generatingIndexRefiner)
              " class="progressbutton" type="primary" disabled>
              <div class="text">准备中...</div>
              <div class="background" :style="{
                width: '100%',
              }"></div>
            </el-button>
            <el-button v-if="state.onProgress &&
              !state.onCancelling &&
              typeof state.progressInfo.generatingIndexBase === 'number' &&
              global.$isEmpty(state.progressInfo.generatingIndexRefiner)
              " class="processingbutton" disabled>
              <div class="text">
                {{ progressPercentageBase + "%" }}
              </div>
              <div class="background" :style="getGeneratingButtonStyleBase"></div>
            </el-button>
            <el-button v-if="state.onProgress &&
              !state.onCancelling &&
              typeof state.progressInfo.generatingIndexRefiner === 'number'
              " class="processingbutton refiner" disabled>
              <div class="text">
                {{ progressPercentageRefiner + "%" }}
              </div>
              <div class="background" :style="getGeneratingButtonStyleRefiner"></div>
            </el-button>
            <el-button v-if="state.onCancelling" class="cancelingbutton" type="primary" disabled>
              <div class="text">取消中...</div>
              <div class="background" :style="{
                width: '100%',
              }"></div>
            </el-button>

            <el-button v-if="state.onProgress" class="cancelbutton" type="primary" @click="handleCancelGenerating"
              :disabled="state.onCancelling || !state.onProgress">
              取消
            </el-button>
          </el-button-group>
          <el-button-group v-else-if="state.progressInfo.isSameUser === false && !state.onCoolingDown
            ">
            <el-button class="processingbutton" disabled>
              <div class="text">占用中...</div>
              <div class="background" :style="getGeneratingButtonStyleBase"></div>
            </el-button>
            <el-button v-if="(state.onProgress || state.onCoolingDown) && !disableQueueing
              " class="cancelbutton" type="primary" @click="handleAddQueuePromise(null)">
              排队
            </el-button>
            <el-button v-else class="cancelbutton" type="primary" @click="handleDeleteQueue()">
              取消排队
            </el-button>
          </el-button-group>

          <el-button-group v-else-if="state.onCoolingDown">
            <el-button class="coolingdownbutton" type="primary" disabled>
              <div class="text">冷却中...</div>
              <div class="background" :style="{
                width: '100%',
              }"></div>
            </el-button>

            <el-button v-if="(state.onProgress || state.onCoolingDown) && !disableQueueing
              " class="cancelbutton" type="primary" @click="handleAddQueuePromise(null)">
              排队
            </el-button>
            <el-button v-else class="cancelbutton" type="primary" @click="handleDeleteQueue()">
              取消排队
            </el-button>
          </el-button-group>
        </a-col>
      </a-row>
      <div class="preview">
        <a-image v-if="global.$isNotEmpty(previewingImage)" :src="previewingImage" fit="contain"
          @click="handleOpenImagePreviewDialog">
          <template #error>
            <el-icon>
              <Picture />
            </el-icon>
          </template>
        </a-image>
        <a-button v-if="!!previewingImage" class="applythisseed" v-model="state.applyThisSeedFlag"
          @click="handleToggleApplySeed">
          采用此种子
        </a-button>
      </div>
      <a-row class="operation" justify="space-between">
        <a-col :span="24">
          <a-button type="primary" @click="handleSaveImage">
            保存到图集
          </a-button>
        </a-col>
      </a-row>
    </el-scrollbar>
    <div class="previewlist_wrapper">
      <h1>暂存区</h1>
      <el-scrollbar>
        <ul>
          <li v-for="(item, index) in currentPreviewList" :key="index" :class="{ active: item.active, saved: item.saved }"
            @click="handleChoosePreview(index)">
            <div v-if="item.generationStatus === 'generating'" class="generating">
              <a-spin :indicator="indicator" />
            </div>
            <div v-else-if="item.generationStatus === 'queueing'" class="generating">
              <a-spin />
            </div>
            <a-image v-else-if="item.generationStatus === 'generated'" width="100%" height="100%" :src="item.base64Data">
            </a-image>

            <el-icon v-if="item.saved" class="savedicon" color="#fff">
              <StarFilled />
            </el-icon>
            <div v-if="item.generationStatus === 'generated'" class="operation">
              <a href="javascript:;" @click.stop="handleDeletePreview(index)">
                <el-icon color="#fff">
                  <Delete />
                </el-icon>
              </a>
            </div>
          </li>
        </ul>
      </el-scrollbar>
    </div>
    <DialogPreviewImage :previewVisible="state.previewImageVisible" :imageUrl="previewDialogData"
      @onCloseDialog="handleClosePreviewImageDialog" />
  </div>
</template>

<script lang="tsx" setup>
import { v4 as uuidv4 } from "uuid";
import DialogPreviewImage from "@/components/DialogPreviewImage.vue";
import { FileImageOutlined } from "@ant-design/icons-vue";

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
  withDefaults,
  h,
} from "vue";

import { LoadingOutlined } from "@ant-design/icons-vue";
import { Picture } from "@element-plus/icons-vue";

import {
  stableDiffusionTxt2ImgBase64DiffuserRequest,
  saveImageToAlbumRequest,
  promptManagementGetRequest,
  promptCategoryManagementGetRequest,
  getCancellingProgressRequest,
  getGenerationStatusRequest,
  checkQueueByUserIdRequest,
  deleteQueueRequest,
  addQueueRequest,
  cancelGenerationRequest,
  getLastImageDataRequest,
  triggerTxt2ImgByQueueRequest,
} from "@/api/stableDiffusion";
import { MouseEventHandler } from "ant-design-vue/es/_util/EventInterface";

const currentInstance = getCurrentInstance() as ComponentInternalInstance;
const global = currentInstance.appContext.config.globalProperties;

const chatScrollbarRef = ref(HTMLDivElement);
const scrollbarRef = ref<InstanceType<typeof ElScrollbar>>();
const loading = ref(true);

interface Props {
  positivePrompt?: string;
  negativePrompt?: string;
  customPositivePrompt?: string;
  customNegativePrompt?: string;
  settings?: any;
  useNegativePrompt?: boolean;
  useRefiner?: boolean;
  useFp32?: boolean;
  useLcmLora?: boolean;
  sampler?: string;
  setSeed?: boolean;
}

const props = withDefaults(defineProps<Props>(), {
  positivePrompt: "",
  customPositivePrompt: "",
  negativePrompt: "",
  customNegativePrompt: "",
  settings: {} as any,
  useNegativePrompt: false,
  useRefiner: false,
  useFp32: false,
  useLcmLora: false,
  sampler: '',
  setSeed: false,
});

const emit = defineEmits<{
  (e: "onChoosePreview", data: any): void;
  (e: "onApplySeed", data: any): void;
}>();

// const loadingInstance = ElLoading.service();
const state = reactive({
  formData: {
    // positivePrompt:
    //   "close-up photography of (grey tabby cat:1. 2) (cuts the fish with a knife on the table:1. 2), (c4ttitude:1. 3), in glasstech kitchen, hyper realistic, intricate detail, (foggy:1. 1), pov from below",
    // positivePrompt:
    //   "Highly detailed portrait of an elegant goddess with ornate clothing and beautiful face blond girl stunningly beautiful, ((open ass)), (perfect ass), smiling, Women Lingerie Lace Mesh Bride Role Play Costume, Set for Cosplay Party, huge boobs, beautiful, stunning, beautiful face , located in beautiful palace bedroom , pearlescent skin, intricate, elegant, highly detailed, (dark shot:1. 17), epic realistic, faded, ((neutral colors)), art, (hdr:1. 5), (muted colors:1. 2), hyperdetailed, (artstation:1. 5), cinematic, warm lights, dramatic light, (intricate details:1. 1), complex background, (rutkowski:0. 8), (teal and orange:0. 4)",
    positivePrompt:
      "masterpiece, concept art, close shot, highly detailed, centered, 1girl in a (shiny color dress) standing in the rain, dreamy cyberpunk girl, cyberpunk art style, cyberpunk beautiful girl, cyberpunk girl, model girl, cyberpunk vibe, beautiful digital artwork, bright cyberpunk glow, cyberpunk vibrant colors, neon rainy cyberpunk setting, cyberpunk vibes, neon rain, cyberpunk art ultrarealistic 8k, has cyberpunk style",
    // positivePrompt:
    //   "8k wallpaper, highly detailed, illustration, 1 girl, long hair, detailed eyes, forrest, hanfu,lakes, soft smile,bamboo,Tea",
    negativePrompt:
      "deformed, bad anatomy, disfigured, poorly drawn face, mutation, mutated, extra limb, ugly, disgusting, poorly drawn hands, missing limb, floating limbs, disconnected limbs, malformed hands, blurry, ((((mutated hands and fingers)))), watermark, watermarked, oversaturated, censored, distorted hands, amputation, missing hands, obese, doubled face, double hands, deformed, bad anatomy, disfigured, poorly drawn face, mutation, mutated, extra limb, ugly, poorly drawn hands, missing limb, floating limbs, disconnected limbs, malformed hands, out of focus, long neck, long body, monochrome, feet out of view, head out of view, lowres, ((bad anatomy)), bad hands, text, error, missing fingers, extra digit, fewer digits, cropped, worst quality, low quality, jpeg artifacts, signature, watermark, username, blurry, artist name, extra limb, poorly drawn eyes, (out of frame), black and white, obese, censored, bad legs, bad hands, text, error, missing fingers, extra digit, fewer digits, cropped, worst quality, low quality, normal quality, jpeg artifacts, signature, watermark, username, blurry, (extra legs), (poorly drawn eyes), without hands, bad knees, multiple shoulders, bad neck",
    numInferenceSteps: 3,
    width: 256,
    height: 256,
  },
  presetSize: {},
  imageData: {},
  imageSrc: "",
  imageInfo: {},
  loading: false,
  progress: "",
  promptList: [] as any,
  positivePromptList: [] as any,
  negativePromptList: [] as any,
  promptCategoryList: [] as any,
  promptIndexData: [] as any,
  loadingFlag: false,
  previewVisible: false,
  positivePromptString: "",
  negativePromptString: "",
  modelInfo: [],
  beginToGenerateFlag: false,
  cancelButtonFlag: false,
  progressInfo: {
    generatingIndexBase: undefined,
    currentTimestepBase: undefined,
    generatingIndexRefiner: undefined,
    currentTimestepRefiner: undefined,
    isSameUser: false,
    temporyLatentImage: "" as string | undefined,
  } as any,
  onProgress: false,
  onCancelling: false,
  onCoolingDown: false,
  preparingFlag: false,
  justRefreshedFlag: true,
  getLastImageFlag: false,
  generatingDisable: true,

  isLooping: false,

  previewImageVisible: false,
  previewPromptVisible: false,
  applyThisSeedFlag: false,
});

const previewStyle = computed(() => {
  return global.$store.state.app.currentWritingFlag;
}) as any;

const currentWritingFlag = computed(() => {
  return global.$store.state.app.currentWritingFlag;
}) as any;

const currentPreviewList = computed(
  () => global.$store.state.app.currentPreviewList
) as any;

const lastPreviewData = computed(() => {
  const length = currentPreviewList.value.length;
  return currentPreviewList.value[length - 1];
}) as any;

const progressPercentageBase = computed(() => {
  return (1000 - state.progressInfo.currentTimestepBase) / 10;
});

const progressPercentageRefiner = computed(() => {
  return (1000 - state.progressInfo.currentTimestepRefiner) / 10;
});

const systemSettings = computed(() => global.$store.state.app.systemSettings);

// const progressPercentageBase = computed(() => {
//   return (
//     (state.progressInfo.generatingIndexBase / state.progressInfo.generatingStepsBase) *
//     100
//   ).toFixed(2);
// });

// const progressPercentageRefiner = computed(() => {
//   return (
//     (state.progressInfo.generatingIndexRefiner /
//       state.progressInfo.generatingStepsRefiner) *
//     100
//   ).toFixed(2);
// });

const previewDialogData = computed(() => {
  const result = currentPreviewList.value.find((item: any) => item.active);
  return result ? result.base64Data : "";
});
const getGeneratingButtonStyleBase = computed(() => {
  return {
    left: -(100 - progressPercentageBase.value) + "%",
  };
}) as any;

const getGeneratingButtonStyleRefiner = computed(() => {
  return {
    left: -(100 - progressPercentageRefiner.value) + "%",
  };
}) as any;

const justRefreshedFlag = computed(
  () => global.$store.state.app.justRefreshedFlag
) as any;

const previewingImage = computed(() => {
  return state.onProgress
    ? state.progressInfo.temporyLatentImage
    : state.imageSrc;
});

const userInfo = computed(() => {
  return global.$store.state.user.userInfo;
});

const disableQueueing = computed(() => {
  return !!currentPreviewList.value.find(
    (item: any) =>
      item.generationStatus === "generating" ||
      item.generationStatus === "queueing"
  );
});

watch(
  () => currentPreviewList.value,
  (newValue: any, oldValue: any) => {
    console.log("watch currentPreviewList.value++++", newValue);
    if (newValue.length === 0) {
      state.imageSrc = "";
    }
  },
  {
    deep: true,
  }
);

const getPreviewIcon = () => {
  return <FileImageOutlined />;
};

const getAppUserId = () => {
  const userComesFrom = userInfo.value.userComesFrom;
  return userComesFrom === "welink"
    ? userInfo.value.welinkUserId
    : userInfo.value.guestUserId;
};

const initGenerationParams = () => {
  console.log(global.$store.state.user);
  const userComesFrom = userInfo.value.userComesFrom;
  const appUserId = getAppUserId();

  state.formData.positivePrompt = mergePromptWords("positive");
  state.formData.negativePrompt = mergePromptWords("negative");

  console.log("props.useNegativePrompt+++++");
  console.log(props.useNegativePrompt);

  const negativePrompt = props.useNegativePrompt ? props.negativePrompt : "";
  const customNegativePrompt = props.useNegativePrompt
    ? props.customNegativePrompt
    : "";
  const numInferenceStepsRefiner = props.useRefiner
    ? props.settings.numInferenceStepsRefiner
    : undefined;
  const seed = props.setSeed ? Number(props.settings.seed) : undefined;
  const sessionId = uuidv4();

  return {
    sessionId,
    positivePrompt: props.positivePrompt,
    customPositivePrompt: props.customPositivePrompt,
    negativePrompt: negativePrompt,
    customNegativePrompt: customNegativePrompt,
    numInferenceSteps: Number(props.settings.numInferenceSteps),
    numInferenceStepsRefiner: numInferenceStepsRefiner,
    width: Number(props.settings.width),
    height: Number(props.settings.height),
    seed: seed,
    useRefiner: props.useRefiner,
    useFp32: props.useFp32,
    useLcmLora: props.useLcmLora,
    sampler: props.sampler,
    appUserId,
    userId: userInfo.value.id,
    userComesFrom,
  } as any;
};

let debounceFlag = true; // 防抖变量
const handleSubmitMessageByDiffuser: MouseEventHandler = async () => {
  if (checkIfOverload()) return;

  setTimeout(() => {
    debounceFlag = true;
  }, 3000);
  if (!debounceFlag) return;
  debounceFlag = false;

  state.beginToGenerateFlag = true;
  await nextTick();
  setTimeout(() => {
    if (!state.isLooping) getGenerationStatusLooper();
  }, 3000);

  const params: any = initGenerationParams();

  console.log("initGenerationParams+++++", params);
  global.$store.commit("app/updateJustRefreshedFlag", false);

  checkIfAddQueuePromise()
    .then(async () => {
      await handleAddQueuePromise(params);

      addOrUpdatePreviewList(
        Object.assign(params, {
          base64Data: "",
          generationStatus: "generating",
        })
      );
      handleChooseLastPreview();
      await nextTick();
      params.active = undefined;
      handleStableDiffusionTxt2ImgBase64Diffuser(params);
    })
    .catch((error: any) => { });
};

const handleStableDiffusionTxt2ImgBase64Diffuser = (params: any) => {
  stableDiffusionTxt2ImgBase64DiffuserRequest(params)
    .then((response: any) => {
      let message: string = "";
      if (response.code === 10000) {
        // 图片上生成完成
        message = response.message;
        params.base64Data = response.data;
        console.log(systemSettings.value.ifBringOutSeed);
        params.seed = response.seed;
        state.imageSrc = response.data;
        params.generationStatus = "generated";

        console.log("stableDiffusionTxt2ImgBase64DiffuserRequest", params);
        addOrUpdatePreviewList(params);
        // 是否自动带出seed
        if (systemSettings.value.ifBringOutSeed) {
          handleChooseLastPreview();
        }
        global.$store.commit("app/cleanGallaryListCacheData");
        state.beginToGenerateFlag = false;
        state.progressInfo = Object.assign(state.progressInfo, {
          generatingIndexBase: undefined,
        });
        state.progressInfo.temporyLatentImage = null;
        deleteQueuePromise({
          sessionId: [global.$getLastOne(currentPreviewList.value).sessionId],
        });
        setTimeout(() => {
          global.$message.success(message);
        }, 1000);
      } else if (response.code === 10001) {
        // 有任务在执行
        message = response.message;
        global.$message.warning(message);
      }
      state.progressInfo.temporyLatentImage = null;
    })
    .catch((error: any) => {
      console.error("error", error);
      const message = error.data.message;

      if (error.data.data) {
        if (error.data.data.code === 10001) {
          global.$message.error(message);
        } else {
          deleteQueuePromise({
            sessionId: [global.$getLastOne(currentPreviewList.value).sessionId],
          });
        }
      } else {
        deleteQueuePromise({
          sessionId: [global.$getLastOne(currentPreviewList.value).sessionId],
        });
      }
      state.onProgress = false;
      state.onCancelling = false;
      state.progressInfo = Object.assign(state.progressInfo, {
        generatingIndexBase: undefined,
      });
      state.progressInfo.temporyLatentImage = undefined;
      global.$message.error(message || "图片生成失败");
      state.beginToGenerateFlag = false;
    });
};

const addQueuePromise = (params: any) => {
  return new Promise((resolve, reject) => {
    addQueueRequest(params)
      .then((response: any) => {
        response = JSON.parse(JSON.stringify(response));

        resolve(response);
      })
      .catch((error: any) => {
        console.log(error);
        reject(error);
      });
  });
};

const handleAddQueueWithCheck = async () => {
  checkIfAddQueuePromise()
    .then(() => {
      handleAddQueuePromise(null);
    })
    .catch((error) => {
      console.log(error);
    });
};

const handleAddQueuePromise: MouseEventHandler = (params: any) => {
  return new Promise(async (resolve, reject) => {
    if (checkIfOverload()) {
      reject();
      return;
    }
    if (
      currentPreviewList.value.find(
        (item: any) =>
          item.generationStatus === "generating" ||
          item.generationStatus === "queueing"
      )
    ) {
      reject({
        message: "已有待执行任务",
      });
      return;
    }

    console.log(userInfo);
    const previewListLength = currentPreviewList.value.length;
    const lastPreview = currentPreviewList.value[previewListLength - 1];
    if (!params) {
      params = initGenerationParams();
      params.generationStatus = "queueing";
    }

    addQueuePromise(params)
      .then((response: any) => {
        if (response.code === 10000) {
          addOrUpdatePreviewList(params);
          handleChooseLastPreview();
          global.$message.success(response.message);
          resolve(response);
        } else if (response.code === 10001) {
          global.$message.warning(response.message);

          const redundantSessionIdData = response.existData
            .filter((item: any) => {
              return item.sessionId !== lastPreviewData.value.sessionId;
            })
            .map((item: any) => item.sessionId);
          deleteQueuePromise({
            sessionId: redundantSessionIdData,
          }).then((response2: any) => {
            resolve(response2);
          });
        }
      })
      .catch((error: any) => {
        console.log(error);
        global.$message.error(error);
        reject(error);
      });
  });
};

const handleDeleteQueue = () => {
  deleteQueuePromise({
    sessionId: [global.$getLastOne(currentPreviewList.value).sessionId],
  })
    .then((response: any) => {
      const deletedSessionId = response.data[0];
      console.log(deletedSessionId);
      console.log(currentPreviewList.value[0].sessionId);
      removeSessionCacheItemBySessionId(deletedSessionId);
    })
    .catch((error: any) => { });
};

const getLastImageDataPromise = () => {
  return new Promise((resolve, reject) => {
    getLastImageDataRequest()
      .then((response: any) => {
        console.log("=====getLastImageDataRequest=====");

        if (response.code === 20000) {
          state.imageSrc = response.data;

          const txt2ImgSessionData = replaceBase64DataBySessionId(
            state.imageSrc,
            response.sessionId
          );
          addOrUpdatePreviewList(txt2ImgSessionData);

          global.$store.commit("app/cleanGallaryListCacheData");
          state.justRefreshedFlag = false;
          resolve(response);
        }
      })
      .catch((error: any) => {
        console.log(error);
        reject();
      })
      .finally(() => {
        state.beginToGenerateFlag = false;
        state.progressInfo.generatingIndexBase = null;
      });
  });
};

const handleSaveImage = () => {
  saveImagePromise()
    .then(() => {
      const tempData = currentPreviewList.value;
      tempData.forEach((item: any) => {
        item.saved = item.active || item.saved;
      });
      global.$store.commit("app/updateCurrentPreviewList", tempData);
      global.$store.commit("app/cleanGallaryListCacheData");
      global.$message.success("保存成功");
    })
    .catch((error: any) => {
      console.log(error);
      global.$message.error("保存失败");
    });
};

const saveImagePromise = () => {
  state.formData.positivePrompt = mergePromptWords("positive");
  state.formData.negativePrompt = mergePromptWords("negative");
  console.log("currentPreviewList+++++++");
  console.log(currentPreviewList.value);
  const chosenPreviewData: any = currentPreviewList.value.find(
    (item: any) => item.active
  );

  return new Promise((resolve, reject) => {
    console.log("userInfo.value");
    console.log(userInfo.value);
    const welinkUserId = userInfo.value.welinkUserId;
    const guestUserId = userInfo.value.guestUserId;
    const userId = userInfo.value.id;
    const userComesFrom = !!welinkUserId ? "welink" : "guest";
    saveImageToAlbumRequest({
      base64Data: state.imageSrc,
      customPositivePrompt: chosenPreviewData.customPositivePrompt,
      positivePrompt: chosenPreviewData.positivePrompt,
      customNegativePrompt: chosenPreviewData.customNegativePrompt,
      negativePrompt: chosenPreviewData.negativePrompt,
      otherSettings: {
        numInferenceSteps: Number(props.settings.numInferenceSteps),
        numInferenceStepsRefiner: props.useRefiner
          ? Number(props.settings.numInferenceStepsRefiner)
          : undefined,
      },
      seed: chosenPreviewData.seed,
      width: Number(props.settings.width),
      height: Number(props.settings.height),
      welinkUserId,
      guestUserId,
      userId,
      userComesFrom,
    })
      .then((response: any) => {
        console.log("saveImageToAlbumRequest+++++", response);
        resolve(response);
      })
      .catch((error: any) => {
        reject(error);
      });
  });
};

const mergePromptWords = (type: string) => {
  let result = "";
  if (type === "positive") {
    state.positivePromptList.forEach((item: any) => {
      result += getActiveTag(item.content).map((item2: any) => item2.value);
    });
  }
  if (type === "negative") {
    state.negativePromptList.forEach((item: any) => {
      result += getActiveTag(item.content).map((item2: any) => item2.value);
    });
  }

  return result;
};

const checkIfOverload = () => {
  const result = currentPreviewList.value.length > 15;
  if (result) {
    global.$message.error("超载");
  }
  return result;
};

const addOrUpdatePreviewList = (data: any) => {
  console.log("addOrUpdatePreviewList");
  console.log(data);
  const sessionId = data.sessionId;
  const currentPreviewListData: any[] = currentPreviewList.value;
  let currentIndex: number | null = null;
  currentPreviewListData.forEach((item: any, index: number) => {
    item.active = false;
    if (item.sessionId === sessionId) {
      currentIndex = index;
    }
  });
  data.active = true;
  if (currentIndex !== null) {
    currentPreviewListData[currentIndex] = data;
  } else {
    currentPreviewListData.push(data);
  }
  global.$store.commit("app/updateCurrentPreviewList", []);
  global.$store.commit("app/updateCurrentPreviewList", currentPreviewListData);

  sessionStorage.setItem(
    "txt2ImgSessionData",
    JSON.stringify(currentPreviewList.value)
  );
};

const deleteQueuePromise = (params: any) => {
  return new Promise((resolve, reject) => {
    deleteQueueRequest({
      sessionId: params.sessionId,
    })
      .then((response: any) => {
        resolve(response);
      })
      .catch((error: any) => {
        console.log(error);
        reject(error);
      });
  });
};

// 此函数判断是否可以添加队列
const checkIfAddQueuePromise = async () => {
  return new Promise((resolve, reject) => {
    checkQueuePromise()
      .then(async (response: any) => {
        if (response.code === 10000) {
          // 整体队列为空
          // await getGenerationStatusPromise();
          resolve(true);
        } else if (response.code === 10001) {
          // 本用户队列为空
          const generationStatusData: any = await getGenerationStatusPromise();

          if (generationStatusData.isSameUser) {
            state.beginToGenerateFlag = true;
          }
          resolve(true);
        } else if (response.code === 10002) {
          // 本用户队列有待执行任务

          const lastTxt2ImgSessionData = lastPreviewData.value;
          let deleteList = [] as any;
          // 查询冗余sessionId
          if (!lastTxt2ImgSessionData) {
            deleteList = response.data;
          } else {
            deleteList = response.data.filter(
              (item: any) =>
                item.data.sessionId !== lastTxt2ImgSessionData.sessionId
            );
          }

          if (deleteList.length === 0) {
            handleStableDiffusionTxt2ImgBase64Diffuser(lastTxt2ImgSessionData);
            if (!state.isLooping) getGenerationStatusLooper();
          } else {
            // 当队列中存在大于1个的队列信息时删除掉多余的
            deleteQueuePromise({
              sessionId: deleteList.map((item: any) => item.data.sessionId),
            })
              .then((response: any) => {
                global.$message.success(response.message);
              })
              .catch((error: any) => {
                console.log(error);
              });
          }
          reject(false);
        }
      })
      .catch((error: any) => { });
  });
};

const checkQueuePromise: any = () => {
  return new Promise((resolve, reject) => {
    checkQueueByUserIdRequest({
      userId: userInfo.value.id,
    })
      .then(async (response: any) => {
        resolve(response);
      })
      .catch((error: any) => {
        reject(error);
      });
  });
};

const getGenerationStatusPromise = () => {
  return new Promise((resolve, reject) => {
    const userId = userInfo.value.id;
    getGenerationStatusRequest({
      userId,
    })
      .then((response: any) => {
        resolve(response);
      })
      .catch((error: any) => {
        console.log(error);
        reject(error);
      });
  });
};

const getGenerationStatusOnce = () => {
  getGenerationStatusPromise()
    .then(async (response: any) => {
      if (
        !response.onProgress &&
        !response.onCancelling &&
        !response.onCoolingDown
      ) {
        setTimeout(() => { }, 3000);
        state.isLooping = false;
        checkQueuePromise();
      }
    })
    .catch((error: any) => {
      console.log(error);
    });
};

const getGenerationStatusLooper = () => {
  state.isLooping = true;
  getGenerationStatusPromise()
    .then(async (response: any) => {
      state.generatingDisable = false;

      state.progressInfo.generatingIndexBase = response.generatingIndexBase;
      state.progressInfo.generatingIndexRefiner =
        response.generatingIndexRefiner;

      state.progressInfo.currentTimestepBase = response.currentTimestepBase;

      state.progressInfo.currentTimestepRefiner =
        response.currentTimestepRefiner;

      state.onProgress = response.onProgress;
      state.progressInfo.isSameUser = response.isSameUser;
      state.onCancelling = response.onCancelling;
      state.onCoolingDown = response.onCoolingDown;

      if (state.onProgress && global.$isNotEmpty(response.temporaryLatent)) {
        state.progressInfo.temporyLatentImage = response.temporaryLatent;
      }
      const interval = state.progressInfo.isSameUser ? 3000 : 3000;

      if (state.onProgress || state.beginToGenerateFlag) {
        if (!state.onProgress) {
        }
        setTimeout(() => {
          getGenerationStatusLooper();
        }, interval);
      } else if (response.onCoolingDown) {
        if (state.justRefreshedFlag && state.getLastImageFlag) {
          getLastImageDataPromise().then((response: any) => {
            deleteQueuePromise({
              sessionId: [response.sessionId],
            });
          });
        }
        setTimeout(() => {
          getGenerationStatusLooper();
        }, interval);
      } else if (response.onCancelling) {
        state.onProgress = false;
        state.isLooping = false;

        // getCancelProgressLooper();
      } else if (
        !response.onProgress &&
        !response.onCancelling &&
        !response.onCoolingDown
      ) {
        state.isLooping = false;
        checkQueuePromise().then((response: any) => {
          if (response.code === 10002) {
            addOrUpdatePreviewList({
              sessionId: global.$getLastOne(currentPreviewList.value).sessionId,
              generationStatus: "generating",
            });

            handleStableDiffusionTxt2ImgBase64Diffuser(response.data[0].data);
            getGenerationStatusLooper();
          }
        });
        setTimeout(() => {
          getGenerationStatusOnce();
        }, 3000);
        // } else if (
        //   response.isSameUser &&
        //   !response.onProgress &&
        //   !response.onCancelling &&
        //   (!state.progressInfo.generatingIndexBase ||
        //     !state.progressInfo.generatingIndexRefiner) &&
        //   justRefreshedFlag.value &&
        //   state.getLastImageFlag
        // ) {
        //   // getLastImageData();
      }

      if (
        justRefreshedFlag.value &&
        response.onProgress &&
        state.progressInfo.isSameUser
      ) {
        state.getLastImageFlag = true;
      }

      if (!response.onProgress && !response.onCancelling) {
        state.beginToGenerateFlag = false;
      }

      global.$store.commit("app/updateCurrentSessionId", response.sessionId);
    })
    .catch((error: any) => {
      console.log(error);
    });
};

const getCancelProgressLooper = () => {
  if (state.onCancelling) {
    setTimeout(() => {
      getCancelProgressPromise()
        .then((response: any) => {
          state.onCancelling = response.status;
          getCancelProgressLooper();
        })
        .catch((error: any) => {
          state.onCancelling = error.data;
        });
    }, 3000);
  } else {
    global.$message.success("进程取消成功");
    state.beginToGenerateFlag = false;
  }
};

const getCancelProgressPromise = () => {
  return new Promise((resolve, reject) => {
    getCancellingProgressRequest()
      .then((response: any) => {
        console.log("=====getCancellingProgressRequest=====");

        resolve(response);
      })
      .catch((error: any) => {
        console.log(error);
        reject(error);
      });
  });
};

const handleChangePresetSize = (item: any) => {
  state.formData.width = item.value[0];
  state.formData.height = item.value[1];
};

const replaceBase64DataBySessionId = (
  base64Data: string,
  sessionId: string
) => {
  let result: any;
  const txt2ImgSessionData: object[] = global.$getTxt2ImgSessionData();
  txt2ImgSessionData.forEach((item: any) => {
    if (item.sessionId === sessionId) {
      result = item;
      result.base64Data = base64Data;
    }
  });

  return result;
};

const handleChooseLastPreview = () => {
  handleChoosePreview(currentPreviewList.value.length - 1);
};

const handleChoosePreview = (index: number) => {
  // customPositivePrompt: props.customPositivePrompt,
  //   customNegativePrompt: props.customNegativePrompt,

  const result = currentPreviewList.value.map((item2: any, index2: number) =>
    Object.assign(item2, {
      active: index === index2,
    })
  );

  if (result.length > 0) {
    state.imageSrc = result[index].base64Data;
    global.$store.commit("app/updateCurrentPreviewList", result);
  } else {
    state.imageSrc = "";
  }
  emit("onChoosePreview", index);
};

const handleDeletePreview = async (index: number) => {
  global.$confirm("确认删除？", "提示", {}).then(() => {
    confirmDeletePreview(index);
  });
};

const handleCancelGenerating: MouseEventHandler = () => {
  state.onCancelling = true;
  state.onProgress = false;
  const activeIndex = currentPreviewList.value.length - 1;
  // removeSessionCacheItemByIndex(activeIndex);
  cancelGenerationRequest().then((response: any) => {
    console.log("cancelGenerationRequest+++++", response);
    console.log("currentPreviewList+++++", currentPreviewList.value);
    const cancellingSessionId = response.sessionId;
    let cancelIndex: number | null = null;
    currentPreviewList.value.forEach((item: any, index: number) => {
      if (item.sessionId === cancellingSessionId) {
        cancelIndex = index;
      }
    });
    console.log(cancellingSessionId);
    console.log(cancelIndex);

    if (cancelIndex !== null) {
      deleteQueuePromise({
        sessionId: [global.$getLastOne(currentPreviewList.value).sessionId],
      });
      removeSessionCacheItemByIndex(cancelIndex);
    }
    // getCancelProgressLooper();
  });
};

const confirmDeletePreview = async (index: number) => {
  global.$store.commit("app/removePreviewByIndex", index);
  await nextTick();
  const activeIndex =
    index === currentPreviewList.value.length
      ? currentPreviewList.value.length - 1
      : index;
  removeSessionCacheItemByIndex(index);
  handleChoosePreview(activeIndex);
};

const removeSessionCacheItemByIndex = (index: number) => {
  const txt2ImgSessionData: object[] = global.$getTxt2ImgSessionData();
  txt2ImgSessionData.splice(index, 1);
  console.log("removeSessionCacheItemByIndex+++++");
  console.log(removeSessionCacheItemByIndex);
  updatePeviewListData(txt2ImgSessionData);
};

const removeSessionCacheItemBySessionId = (sessionId: string) => {
  const txt2ImgSessionData: object[] = global.$getTxt2ImgSessionData();

  let deleteIndex;
  txt2ImgSessionData.forEach((item: any, index: number) => {
    if (item.sessionId === sessionId) deleteIndex = index;
  });
  if (deleteIndex !== undefined) {
    txt2ImgSessionData.splice(deleteIndex, 1);
    console.log("removeSessionCacheItemByIndex+++++");
    console.log(txt2ImgSessionData);
    updatePeviewListData(txt2ImgSessionData);
  }
};

const updatePeviewListData = (data: any[]) => {
  let currentPreviewListData: any[] = currentPreviewList.value;
  currentPreviewListData = data;
  global.$store.commit("app/updateCurrentPreviewList", currentPreviewListData);
  sessionStorage.setItem(
    "txt2ImgSessionData",
    JSON.stringify(currentPreviewList.value)
  );
};

const getPromptListPromise = () => {
  return new Promise((resolve, reject) => {
    promptManagementGetRequest({})
      .then((response: any) => {
        resolve(response.data);
      })
      .catch((error: any) => {
        reject(error);
      });
  });
};

const getPromptCategoryListPromise = () => {
  return new Promise((resolve, reject) => {
    promptCategoryManagementGetRequest({})
      .then((response: any) => {
        resolve(response.data);
      })
      .catch((error: any) => {
        reject(error);
      });
  });
};

const handleChoosePrompt = (item: any) => {
  item.active = !item.active;
};

const getPromptsByCategory: any = (item: any) => {
  return state.promptList.filter((item2: any) => item2.category === item.value);
};

const getActiveTag = (promptList: any) => {
  if (!promptList) return [];
  return promptList.filter((item: any) => item.active);
};

const handleCloseTag = (data: any) => {
  console.log(state.promptIndexData);

  state.promptIndexData.forEach((item1: any) => {
    item1.content.forEach((item2: any) => {
      if (item2.id === data.id) {
        item2.active = false;
      }
    });
  });
};

const handlePreviewPrompt = () => {
  let positivePromptString = "";
  let negativePromptString = "";
  state.positivePromptList.forEach((item: any) => {
    positivePromptString += getActiveTag(item.content).map(
      (item2: any) => item2.value
    );
  });
  state.negativePromptList.forEach((item: any) => {
    positivePromptString += getActiveTag(item.content).map(
      (item2: any) => item2.value
    );
  });
  state.positivePromptString = positivePromptString;
  state.negativePromptString = negativePromptString;
  state.previewPromptVisible = true;
};

const handleClosePromptPreviewDialog = () => {
  state.previewPromptVisible = false;
};

const handleOpenImagePreviewDialog = () => {
  // state.previewImageVisible = true;
};

const handleClosePreviewImageDialog = () => {
  state.previewImageVisible = false;
};

const handleToggleApplySeed: void = async (data: boolean) => {
  global.$message.success("已采用此种子");
  let currentSeed: number | null = null;
  if (data) {
    const currentPreviewListData: any[] = currentPreviewList.value;
    currentSeed = currentPreviewListData.find((item: any) => item.active).seed;
  }

  emit("onApplySeed", 0);
  await nextTick();
  emit("onApplySeed", currentSeed);
};

const indicator = h(LoadingOutlined, {
  style: {
    fontSize: "50px",
  },
  spin: true,
});

onMounted(async () => {
  checkIfAddQueuePromise();
  getGenerationStatusLooper();
  const applySettingsUsed = global.$store.state.app.applySettingsUsed;
  handleChooseLastPreview();

  if (applySettingsUsed) {
    setTimeout(() => { }, 500);
  }
});

onBeforeUnmount(() => {
  // global.$store.commit("app/updateCurrentPreviewList", []);
  state.onProgress = false;
});
</script>

<style lang="scss">
.preview_container {
  display: flex;
  width: 40%;
  height: 100%;

  .preview_wrapper {
    display: inline-block;
    flex: 1;
    height: 100%;
    overflow: auto;
    box-sizing: border-box;

    .button_item {
      margin: 0.4rem 0.5rem 0 0.5rem;
      text-align: center;

      .el-button-group,
      .ant-btn-group {
        display: flex;
        border-radius: 5px;
      }

      .el-button-group {
        // border: 1px solid rgba(64, 158, 255);
      }

      button {
        width: 100%;
        height: 2rem;
        overflow: hidden;
      }

      .cancelbutton {
        display: inline-block;
        width: 2rem;
        z-index: 333;
        position: relative;
        border: 0;

        span {
          display: inline-block;
          width: 100%;
          height: 100%;
          line-height: 1.7rem;
          position: relative;
        }
      }

      .processingbutton {
        display: inline-block;
        vertical-align: middle;
        position: relative;
        padding: 0;

        span {
          display: flex;
          width: 100%;
          height: 100%;
          font-size: 0;

          .text {
            display: inline-block;
            position: relative;
            font-size: 0.5rem;
            width: 100%;
            height: 0.5rem;
            line-height: 0.5rem;
            padding: 0.2rem 0;
            z-index: 1;
            color: #fff;
            background-color: #000;
          }

          .background {
            display: inline-block;
            width: 100%;
            height: 100%;
            position: absolute;
            background-color: red;
            animation: animate 8s linear infinite;
            background-image: repeating-linear-gradient(110deg,
                #000 0%,
                #000 4%,
                red 4.1%,
                red 8.6%);
            top: 0;
            left: 0;
            transition: all 0.3s;
          }
        }

        &.refiner {
          .background {
            background-image: repeating-linear-gradient(110deg,
                #000 0%,
                #000 4%,
                yellow 4.1%,
                yellow 8.6%);
          }
        }
      }

      .progressbutton {
        display: inline-block;
        width: 100%;
        padding: 0;
        border: 0;

        span {
          display: flex;
          width: 100%;
          height: 100%;
          position: relative;
          justify-content: center;

          .text {
            display: inline-block;
            width: 100%;
            padding: 0.3rem;
            z-index: 1;
            position: relative;
            font-size: 0.4rem;
            letter-spacing: 0.1rem;
            color: #fff;
            background-color: rgba($color: #000000, $alpha: 1);
          }

          .background {
            display: inline-block;
            width: 100%;
            height: 100%;
            animation: animate 8s linear infinite;
            background-image: repeating-linear-gradient(110deg,
                #000 0%,
                #000 4%,
                rgb(64, 158, 255) 4.1%,
                rgb(64, 158, 255) 8.6%);
            position: absolute;
            top: 0;
            left: 0;
          }

          .preparingbutton {
            display: inline-block;
            vertical-align: middle;
            position: relative;
          }
        }
      }

      .cancelingbutton {
        display: inline-block;
        width: 100%;
        padding: 0;

        span {
          display: flex;
          width: 100%;
          height: 100%;
          position: relative;
          justify-content: center;

          .text {
            display: inline-block;
            width: 100%;
            padding: 0.3rem;
            z-index: 1;
            position: relative;
            font-size: 0.4rem;
            letter-spacing: 0.1rem;
            color: #fff;
            background-color: rgba(42, 89, 138);
          }

          .background {
            display: inline-block;
            width: 100%;
            height: 100%;
            background-image: repeating-linear-gradient(110deg,
                #ff6a00 0%,
                #ff6a00 4%,
                rgb(0, 102, 255) 4.1%,
                rgb(0, 102, 255) 8.6%);
            animation: animate 8s linear infinite;

            position: absolute;
            top: 0;
            left: 0;
          }

          .preparingbutton {
            display: inline-block;
            vertical-align: middle;
            position: relative;
          }
        }
      }

      .coolingdownbutton {
        display: inline-block;
        width: 100%;
        padding: 0;

        span {
          display: flex;
          width: 100%;
          height: 100%;
          position: relative;
          justify-content: center;

          .text {
            display: inline-block;
            width: 100%;
            padding: 0.3rem;
            z-index: 1;
            position: relative;
            font-size: 0.4rem;
            letter-spacing: 0.1rem;
            color: #fff;
            background-color: rgba(42, 89, 138);
          }

          .background {
            display: inline-block;
            width: 100%;
            height: 100%;
            background-image: repeating-linear-gradient(110deg,
                #00ff2f 0%,
                #00ff2f 4%,
                #000 4.1%,
                #000 8.6%);
            animation: animate 8s linear infinite;

            position: absolute;
            top: 0;
            left: 0;
          }

          .preparingbutton {
            display: inline-block;
            vertical-align: middle;
            position: relative;
          }
        }
      }
    }

    .preview {
      flex: 1;
      margin: 0.5rem 0.6rem 0 0.5rem;
      padding: 0.4rem;
      width: calc(100% - 1rem);
      height: 15rem;
      min-height: 10rem;
      overflow: hidden;
      box-sizing: border-box;
      border: 1px solid #666;
      position: relative;

      &:before {
        content: "";
        display: inline-block;
        width: 0;
        height: 100%;
        vertical-align: middle;
      }

      &:hover {
        .applythisseed {
          opacity: 1;
        }
      }

      .ant-image {
        width: 100%;

        .ant-image-img {
          width: 100%;
          height: 100%;
        }
      }

      .applythisseed {
        position: absolute;
        top: 1rem;
        right: 0.5rem;
        opacity: 0;
      }

      .common_progress_item {
        display: inline-block;
        vertical-align: middle;
      }
    }

    .operation {
      margin: 0.5rem;
      height: 3rem;
    }
  }

  .previewlist_wrapper {
    display: flex;
    flex-direction: column;
    // margin: 0 0 0 0.3rem;
    width: 3.7rem;
    height: 100%;
    // height: 600px;

    border-left: 1px solid #666;

    // border-right: 1px solid #666;
    h1 {
      font-size: 0.4rem;
      margin: 0;
      padding: 0.2rem 0;
      font-weight: normal;
      text-align: center;
      color: #000;
    }

    .el-scrollbar {
      flex: 1;

      ul {
        width: 100%;
        height: 100%;

        li {
          // margin: 0.3rem 0 0 0;
          margin: 0;
          margin: 0 0.3rem 0.3rem 0.3rem;
          width: 3rem;
          height: 3rem;
          border-style: solid;
          border-width: 2px;
          border-color: transparent;
          transition: all 0.3s;
          position: relative;

          .savedicon {
            display: inline-block;
            position: absolute;
            left: 0;
            top: 0;
            font-size: 0.8rem;
          }

          .el-image {
            width: 100%;
            height: 100%;
          }

          .generating {
            display: flex;
            width: 100%;
            height: 100%;
            text-align: center;
            align-items: center;

            >div {
              width: 100%;
            }
          }

          .operation {
            position: absolute;
            left: 0;
            top: 0;
            width: 100%;
            height: 100%;
            opacity: 0;
            transition: all 0.3s;
            text-align: right;

            a {
              display: inline-block;

              .el-icon {
                margin: 0.1rem;
                font-size: 0.5rem;
              }
            }
          }

          &:hover {
            .operation {
              opacity: 1;
            }
          }

          &.active {
            border-color: #000;
          }
        }
      }
    }
  }

  @keyframes animate {
    0% {}

    100% {
      background-position: 590px 0;
    }
  }
}
</style>
