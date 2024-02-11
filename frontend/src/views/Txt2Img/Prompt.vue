<template>
  <div class="prompt_container">
    <!-- <el-tabs class="prompt_wrapper" tab-position="left">
      <el-tab-pane
        :label="item1.title"
        v-for="(item1, index1) in state.imageContentCategoryList"
        :key="index1"
      >
      </el-tab-pane>
    </el-tabs> -->
    <div class="prompt_wrapper">
      <el-tabs class="promitdirectiontabs" type="card">
        <el-tab-pane label="正向">
          <el-scrollbar v-loading="state.loadingFlag">
            <li class="block" v-for="(item2, index2) in state.positivePromptListWithCategory" :key="index2">
              <h5>
                <span>{{ item2.title }}</span>
                <el-checkbox v-model="item2.checkAll" :indeterminate="item2.checkAll === 'intermediate'"
                  @change="handleCheckCheckAll($event, item2)">
                  全选
                </el-checkbox>
              </h5>
              <ul class="content">
                <li v-for="(item3, index3) in item2.content" :key="item3.id" :class="{ active: item3.active }">
                  <a-button :type="item3.active ? 'primary' : undefined" @click="
                    handleChoosePositivePrompt(item2, item3, index2, index3)
                    ">
                    {{ item3.title }}
                  </a-button>
                </li>
              </ul>
            </li>
          </el-scrollbar>
        </el-tab-pane>
        <el-tab-pane label="反向">
          <el-scrollbar v-loading="state.loadingFlag">
            <li class="block" v-for="(item2, index2) in state.negativePromptListWithCategory" :key="item2.id">
              <h5>
                <span>{{ item2.title }}</span>
                <el-checkbox v-model="item2.checkAll" :indeterminate="item2.checkAll === 'intermediate'"
                  @change="handleCheckCheckAll($event, item2)">
                  全选
                </el-checkbox>
              </h5>
              <ul class="content">
                <li v-for="(item3, index3) in item2.content" :key="item3.id" :class="{ active: item3.active }">
                  <a-button :type="item3.active ? 'primary' : undefined" @click="
                    handleChooseNegativePrompt(item2, item3, index2, index3)
                    ">
                    {{ item3.title }}
                  </a-button>
                </li>
              </ul>
            </li>
          </el-scrollbar>
        </el-tab-pane>
      </el-tabs>
    </div>

    <el-scrollbar class="setting">
      <el-form class="input_container" ref="formDataRef" label-position="left" :model="state.formData">
        <div class="content">
          <div class="header">
            <a-button class="previewprompt" type="primary" @click="handlePreviewPrompt">
              预览提示词
            </a-button>
          </div>

          <el-tabs type="border-card">
            <el-tab-pane>
              <template #label>
                <div class="positiveprompttablabel">
                  <span class="checkbox">
                    <el-checkbox v-model="isUsingCustomPsitivePrompt"></el-checkbox>
                  </span>
                  <span class="label">&nbsp&nbsp自定义提示词 </span>
                </div>
              </template>
              <el-input type="textarea" :rows="5" clearable autocomplete="off" v-model="state.customPositivePrompt"
                @change="handleChangeCustomPositivePrompt" :placeholder="submitInputPlaceholder"></el-input>
            </el-tab-pane>
            <el-tab-pane>
              <template #label>
                <div class="positiveprompttablabel">
                  <span class="checkbox">
                    <el-checkbox v-model="isUsingOptionalPositivePrompt"></el-checkbox>
                  </span>
                  <span class="label">&nbsp&nbsp选项提示词 </span>
                </div>
              </template>
              <el-scrollbar class="promptarea" max-height="6rem">
                <ul v-for="(
                    item1, index1
                  ) in state.positivePromptListWithCategory" :key="item1.id">
                  <li v-for="(item2, index2) in getActiveTag(item1.content)" :key="item2.id">
                    <a-tag :key="item2.id" closable bordered :color="item1.color" @close="handleCloseTag(item2)">
                      {{ item2.title }}
                    </a-tag>
                  </li>
                </ul>
              </el-scrollbar>
            </el-tab-pane>
          </el-tabs>
        </div>
        <el-collapse v-model="state.collapsedSettings" @change="handleChangeCollpase" class="content">
          <el-collapse-item title="使用反向提示词" name="useNegativePrompt" class="settingitem">
            <template #title>
              <el-form-item>
                <div class="settingitemcontent">
                  <span class="switchertitle">使用反向提示词</span>
                  <div class="switcher">
                    <el-switch :value="state.useNegativePrompt" style="--el-switch-on-color: #13ce66">
                    </el-switch>
                  </div>
                </div>
              </el-form-item>
            </template>
            <div class="content">
              <el-tabs type="border-card">
                <el-tab-pane>
                  <template #label>
                    <div class="positiveprompttablabel">
                      <span class="checkbox">
                        <el-checkbox v-model="isUsingCustomNegativePrompt"></el-checkbox>
                      </span>
                      <span class="label">&nbsp&nbsp自定义反向提示词 </span>
                    </div>
                  </template>
                  <el-input type="textarea" :rows="5" clearable autocomplete="off" v-model="state.customNegativePrompt"
                    @change="handleChangeCustomNegativePrompt" :placeholder="submitInputPlaceholder"></el-input>
                </el-tab-pane>
                <el-tab-pane>
                  <template #label>
                    <div class="positiveprompttablabel">
                      <span class="checkbox">
                        <el-checkbox v-model="isUsingOptionalNegativePrompt"></el-checkbox>
                      </span>
                      <span class="label">&nbsp&nbsp选项反向提示词 </span>
                    </div>
                  </template>
                  <el-scrollbar class="promptarea" max-height="6rem">
                    <ul v-for="(
                        item1, index1
                      ) in state.negativePromptListWithCategory" :key="index1">
                      <li v-for="item2 in getActiveTag(item1.content)" :key="item2.id">
                        <a-tag :key="item2.id" closable bordered :color="item1.color" @close="handleCloseTag(item2)">
                          {{ item2.title }}
                        </a-tag>
                      </li>
                    </ul>
                  </el-scrollbar>
                </el-tab-pane>
              </el-tabs>
            </div>
          </el-collapse-item>

          <el-collapse-item title="指定种子" name="setSeed" class="settingitem">
            <template #title>
              <el-form-item>
                <div class="settingitemcontent">
                  <span class="switchertitle">指定种子</span>
                  <div class="switcher">
                    <el-switch :value="state.setSeed" style="--el-switch-on-color: #13ce66"
                      @change="emitOnSettingChanged">
                    </el-switch>
                  </div>
                </div>
              </el-form-item>
            </template>
            <div class="content">
              <a-row>
                <a-col :span="23">
                  <el-form-item label="种子">
                    <el-input v-model.number="state.formData.seed" type="number"></el-input>
                  </el-form-item>
                </a-col>
              </a-row>
            </div>
          </el-collapse-item>
          <el-collapse-item title="使用反向提示词" name="useRefiner" class="userefuner settingitem">
            <template #title>
              <el-form-item>
                <div class="settingitemcontent">
                  <span class="switchertitle">使用Refiner</span>
                  <div class="switcher">
                    <el-switch :value="state.useRefiner" @change="handleChangeUseRefiner"
                      style="--el-switch-on-color: #13ce66">
                    </el-switch>
                  </div>
                </div>
              </el-form-item>
            </template>
            <div class="content">
              <a-row>
                <a-col :span="24">
                  <el-form-item label="步数">
                    <el-slider v-model="state.formData.numInferenceStepsRefiner" :max="200" :min="5" show-input
                      size="small" :marks="stepMarks" />
                  </el-form-item>
                </a-col>
              </a-row>
            </div>
          </el-collapse-item>
        </el-collapse>

        <el-form class="form" ref="formDataRef" label-position="top" label-width="60px">
          <a-row :gutter="10">
            <a-col :span="24">
              <el-form-item label="预设比例">
                <ul class="ratiosettings">
                  <li v-for="(item, index) in state.ratioSettingsDictionary" :key="index"
                    :class="(item.active ? 'active ' : ' ') + item.name" @click="handleChooseRatio(index)">
                    <div class="outer">
                      <div class="inner">
                        <span class="lefttop"></span>
                        <span class="righttop"></span>
                        <span class="rightbottom"></span>
                        <span class="leftbottom"></span>
                      </div>
                    </div>
                  </li>
                </ul>
              </el-form-item>
            </a-col>
          </a-row>
          <a-row>
            <a-col :span="24">
              <el-form-item label="预设尺寸">
                <div class="imageratio">
                  <ul>
                    <li v-for="(item, index) in state.sizePresetListTop" :key="index"
                      :class="{ active: checkSizeActive(item) }" @click="handleChooseSize(item)">
                      <a-button :type="checkSizeActive(item) ? 'primary' : ''">
                        {{ item }}
                      </a-button>
                    </li>
                  </ul>
                  <ul>
                    <li v-for="(item, index) in state.sizePresetListBottom" :key="index" @click="handleChooseSize(item)">
                      <a-button :type="checkSizeActive(item) ? 'primary' : ''">
                        {{ item }}
                      </a-button>
                    </li>
                  </ul>
                </div>
              </el-form-item>
            </a-col>
          </a-row>
          <a-row>
            <a-col :span="24">
              <el-form-item :label="'宽度'">
                <el-slider v-model="state.formData.width" :max="6144" :min="320" show-input size="small" />
              </el-form-item>
            </a-col>
          </a-row>
          <a-row>
            <a-col :span="24">
              <el-form-item label="高度">
                <el-slider v-model="state.formData.height" :max="6144" :min="320" show-input size="small" />
              </el-form-item>
            </a-col>
          </a-row>
          <a-row class="steps">
            <a-col :span="24">
              <el-form-item label="步数">
                <el-slider v-model="state.formData.numInferenceSteps" :max="state.useLcmLora ? 8 : 200"
                  :min="state.useLcmLora ? 1 : 3" show-input size="small" :marks="stepMarks" />
              </el-form-item>
            </a-col>
          </a-row>

          <a-row class="settingitem">
            <a-col :span="24">
              <el-form-item>
                <div class="settingitemcontent">
                  <span class="switchertitle">使用fp32</span>
                  <div class="switcher">
                    <el-switch v-model="state.useFp32" @change="emitOnSettingChanged"
                      style="--el-switch-on-color: #13ce66">
                    </el-switch>
                  </div>
                </div>
              </el-form-item>

            </a-col>
          </a-row>
          <a-row class="settingitem">
            <a-col :span="24">
              <el-form-item>
                <div class="settingitemcontent">
                  <span class="switchertitle">使用LCM LoRA</span>
                  <div class="switcher">
                    <el-switch v-model="state.useLcmLora" @change="handleChangeUseLcmLora"
                      style="--el-switch-on-color: #13ce66">
                    </el-switch>
                  </div>
                </div>
              </el-form-item>


            </a-col>
          </a-row>
          <a-row class="settingitem">
            <a-col :span="24">
              <el-form-item>
                <div class="settingitemcontent">
                  <span class="switchertitle">采样器</span>
                  <div class="select">
                    <a-select ref="select" v-model:value="state.sampler" @change="handleChangeSampler">
                      <a-select-option v-for="item in global.$store.state.dictionary.samplerDictionary"
                        :value="item.value">{{ item.label }}</a-select-option>
                    </a-select>
                  </div>
                </div>
              </el-form-item>

            </a-col>
          </a-row>
        </el-form>



      </el-form>
    </el-scrollbar>

    <DialogPreviewPrompt :previewPromptVisible="state.previewPromptVisible"
      :customPositivePrompt="state.customPositivePrompt" :positivePromptList="state.positivePromptListWithCategory"
      :customNegativePrompt="state.customNegativePrompt" :negativePromptList="state.negativePromptListWithCategory"
      :useNegativePrompt="state.useNegativePrompt" :width="state.formData.width" :height="state.formData.height"
      :numInferenceSteps="state.formData.numInferenceSteps" :useRefiner="state.useRefiner"
      :numInferenceStepsRefiner="state.formData.numInferenceStepsRefiner" :setSeed="state.setSeed"
      :seed="state.formData.seed" @onCloseDialog="handleClosePreviewDialog" />
  </div>
</template>

<script lang="tsx" setup>
import {
  reactive,
  watch,
  computed,
  onMounted,
  onActivated,
  onDeactivated,
  onBeforeUnmount,
  getCurrentInstance,
  ComponentInternalInstance,
  ref,
  nextTick,
} from "vue";


import DialogPreviewPrompt from "./DialogPreviewPrompt.vue";

import {
  promptManagementGetRequest,
  promptCategoryManagementGetRequest,
  modelManagemenGetRequest,
} from "@/api/stableDiffusion";

import { dictionaryManagementGetRequest } from "@/api/dictionary";
import { v4 as uuidv4 } from "uuid";
// SelectValue
// DefaultOptionType
const currentInstance = getCurrentInstance() as ComponentInternalInstance;
const global = currentInstance.appContext.config.globalProperties;
const {
  proxy: { $forceUpdate },
}: any = getCurrentInstance();

interface Props {
  currentPreviewIndex?: number | null;
  appliedSeed?: number | null;
}

const props = withDefaults(defineProps<Props>(), {
  currentPreviewIndex: null,
  appliedSeed: 0,
});

const emit = defineEmits<{
  (e: "onPositivePromptChanged", data: any): void;
  (e: "onCustomPositivePromptChanged", data: any): void;
  (e: "onNegativePromptChanged", data: any): void;
  (e: "onCustomNegativePromptChanged", data: any): void;
  (e: "onSettingChanged", data: any): void;
  (e: "onChangeUseNegativePrompt", data: any): void;
}>();

// currentPreviewIndex

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
    numInferenceSteps: 5,
    numInferenceStepsRefiner: 5,
    width: 320,
    height: 320,
    seed: undefined as undefined | number,
  },
  promptTabActive: "positive",
  promptList: [] as any,
  imageData: {},
  imageSrc: "",
  imageInfo: {},
  loading: false,
  progress: "",
  positivePromptList: [] as any,
  negativePromptList: [] as any,
  positivePromptListWithCategory: [] as any,
  negativePromptListWithCategory: [] as any,
  promptCategoryList: [] as any,
  promptIndexData: [] as any,
  loadingFlag: false,
  previewPromptVisible: false,
  positivePromptString: "",
  negativePromptString: "",
  modelInfo: [] as any,
  beginToGenerateFlag: false,
  onProgress: false,
  cancelButtonFlag: false,
  progressbarFlag: false,
  progressInfo: {
    generatingIndex: undefined,
    generatingSteps: undefined,
  },
  hoverProgressbarFlag: false,
  cancellingFlag: false,
  preparingFlag: false,
  getLastImageFlag: false,
  generatingDisable: true,
  generationStatus: {
    onCancelling: false,
    onProgress: false,
    generatingIndex: null,
    generatingSteps: null,
  },

  customPositivePrompt: "",
  customNegativePrompt: "",

  ratioSettingsDictionary: [
    {
      name: "onetoone",
      active: true,
      sizeList: [
        "512:512",
        "960:960",
        "1024:1024",
        "1280:1280",
        "2560:2560",
        "4096:4096",
      ],
    },
    {
      name: "tentofifteen",
      active: false,
      sizeList: ["512:768", "768:1152", "1024:1536", "2048:3072", "4096:6144"],
    },
    {
      name: "fifteentoten",
      active: false,
      sizeList: ["768:512", "1152:768", "1536:1024", "3072:2048", "6144:4096"],
    },
  ],
  previewPositivePromptsTabsActive: false,
  chosenPreviewIndex: 0,

  sizePresetListTop: [] as any,
  sizePresetListBottom: [] as any,
  collapsedSettings: [],
  useNegativePrompt: false,
  useRefiner: false,
  useFp32: false,
  useLcmLora: false,
  sampler: 'DPM++ 2M Karras',
  setSeed: false,
  imageContentCategoryList: [] as any,
});

const promptListCacheData = computed(() => {
  return global.$store.state.app.promptListCacheData;
}) as any;

const promptCategoryListCacheData = computed(() => {
  return global.$store.state.app.promptCategoryListCacheData;
}) as any;

const submitInputPlaceholder = computed(() => {
  return global.$isMobile() ? "" : "";
}) as any;

const currentPreviewList = computed(
  () => global.$store.state.app.currentPreviewList
) as any;

const stepMarks = computed(() => {
  const range = 305 - 5;
  const result = {} as any;
  const marksCount = 6;
  const step = range / marksCount;
  for (let index = 0; index < marksCount; index++) {
    result[step * (index + 1)] = step * (index + 1) + "";
  }
  return result;
}) as any;

const isUsingCustomPsitivePrompt = computed(() => {
  return global.$isNotEmpty(state.customPositivePrompt);
});

const isUsingOptionalPositivePrompt = computed(() => {
  let result = false;
  state.positivePromptListWithCategory.forEach((item: any) => {
    if (!result && item.content) {
      if (item.content.filter((item2: any) => item2.active).length > 0) {
        result = true;
      }
    }
  });
  return result;
});

const isUsingCustomNegativePrompt = computed(() => {
  return global.$isNotEmpty(state.customNegativePrompt);
});

const isUsingOptionalNegativePrompt = computed(() => {
  let result = false;
  state.negativePromptListWithCategory.forEach((item: any) => {
    if (!result && item.content) {
      if (item.content.filter((item2: any) => item2.active).length > 0) {
        result = true;
      }
    }
  });
  return result;
});

watch(
  () => state.formData.width,
  (newValue: any, oldValue: any) => {
    console.log("waatch state.formData.width++++", newValue);
  }
);

watch(
  () => state.useNegativePrompt,
  (newValue: any, oldValue: any) => {
    state.collapsedSettings = state.collapsedSettings.filter(
      (item: string) => item !== "" && item !== "useNegativePrompt"
    );
    if (newValue) {
      state.collapsedSettings.push("useNegativePrompt");
    }
  }
);

watch(
  () => state.useRefiner,
  (newValue: any, oldValue: any) => {
    state.collapsedSettings = state.collapsedSettings.filter(
      (item: string) => item !== "" && item !== "useRefiner"
    );
    if (newValue) {
      state.collapsedSettings.push("useRefiner");
    }
  }
);


watch(
  () => state.setSeed,
  (newValue: any, oldValue: any) => {
    state.collapsedSettings = state.collapsedSettings.filter(
      (item: string) => item !== "" && item !== "setSeed"
    );
    if (newValue) {
      state.collapsedSettings.push("setSeed");
    }
  }
);

watch(
  () => currentPreviewList.value,
  (newValue: any, oldValue: any) => {
    newValue.forEach((item: any, index: number) => {
      if (item.active) {
        state.chosenPreviewIndex = index;
        initCachedSettingData(index);
        emitPositivePromptString();
        emitNegativePromptString();
        emitOnSettingChanged();
      }
    });
  }
);

watch(
  () => props.appliedSeed,
  (newValue: any, oldValue: any) => {
    console.log("props.appliedSeed+++++", newValue);
    state.setSeed = true;
    state.formData.seed = newValue;
  }
);

const getImageCategoryDictionaryPromise = () => {
  return new Promise((resolve, reject) => {
    dictionaryManagementGetRequest({
      category: "imageContentCategory",
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

const getPresetSizeTop = () => {
  let activeItem: any = state.ratioSettingsDictionary.find(
    (item: any) => item.active
  );
  activeItem = !!activeItem ? activeItem : { sizeList: [] };
  return activeItem.sizeList.filter((item: any, index: number) => index < 3);
};

const getPresetSizeBottom = () => {
  let activeItem: any = state.ratioSettingsDictionary.find(
    (item: any) => item.active
  );
  activeItem = !!activeItem ? activeItem : { sizeList: [] };
  return activeItem.sizeList.filter((item: any, index: number) => index > 2);
};

const handleChoosePositivePrompt = async (
  item2: any,
  item3: any,
  index2: number,
  index3: number
) => {
  const active: boolean =
    state.positivePromptListWithCategory[index2].content[index3].active;
  state.positivePromptListWithCategory[index2].content[index3].active = !active;

  emitPositivePromptString();
  item2.checkAll = checkIfCheckAll("positive", item2.value);
};

const handleChooseNegativePrompt = (
  item2: any,
  item3: any,
  index2: number,
  index3: number
) => {
  const active: boolean =
    state.negativePromptListWithCategory[index2].content[index3].active;
  state.negativePromptListWithCategory[index2].content[index3].active = !active;
  emitNegativePromptString();

  item2.checkAll = checkIfCheckAll("negative", item3.value);
};

const handleCheckCheckAll = (event: any, item1: any) => {
  item1.content.forEach((item2: any) => {
    if (typeof event === "boolean") {
      item2.active = event;
    } else {
      item2.active = false;
    }
  });
  emitPositivePromptString();
  emitNegativePromptString();
};

const getData = () => {
  return new Promise(async (resolve: any, reject: any) => {
    try {
      if (
        promptListCacheData.value.length === 0 ||
        promptCategoryListCacheData.value.length === 0
      ) {
        console.warn("save cache!!!!");
        state.loadingFlag = true;
        state.imageContentCategoryList =
          await getImageCategoryDictionaryPromise();
        const promptList = await promptManagementGetRequest({});
        state.promptList = promptList.data.map((item: any) => {
          return Object.assign(item, {
            value: item.value.trim(),
          });
        });
        const promptCategoryList = await promptCategoryManagementGetRequest({});
        state.promptCategoryList = promptCategoryList.data;
        global.$store.commit("app/updatePromptListCacheData", state.promptList);
        global.$store.commit(
          "app/updatePromptCategoryListCacheData",
          state.promptCategoryList
        );
        resolve();
      } else {
        console.warn("cached!!!!");
        state.promptList = promptListCacheData.value;
        state.promptCategoryList = promptCategoryListCacheData.value;
        resolve();
      }
    } catch (error) {
      reject(error);
    }
  });
};

const initRandomPromptColor = () => {
  let result = [] as string[];
  const tagTypeDictionary: any[] = global.$store.state.app.tagTypeDictionary;
  const randomList = global.$generateRandom(tagTypeDictionary.length);
  let randomListIndex = 0;
  state.positivePromptListWithCategory.forEach((item: any) => {
    if (randomListIndex === randomList.length) {
      randomListIndex = 0;
    }
    item.color =
      global.$store.state.app.tagTypeDictionary[randomList[randomListIndex]];
    randomListIndex++;
  });
  state.negativePromptListWithCategory.forEach((item: any) => {
    if (randomListIndex === randomList.length) {
      randomListIndex = 0;
    }
    item.color =
      global.$store.state.app.tagTypeDictionary[randomList[randomListIndex]];
    randomListIndex++;
  });

  return result;
};

const initData = async () => {
  const positivePromptList = state.promptList.filter(
    (item: any) => item.direction === "positive"
  );
  const negativePromptList = state.promptList.filter(
    (item: any) => item.direction === "negative"
  );

  const positivePromptListWithCategory = JSON.parse(
    JSON.stringify(
      state.promptCategoryList.filter((item1: any) => {
        return (
          positivePromptList.filter(
            (item2: any) => item2.category === item1.value
          ).length > 0
        );
      })
    )
  );

  positivePromptListWithCategory.forEach((item: any) => {
    item.checkAll = false;
    item.content = positivePromptList
      .filter((item2: any) => item2.category === item.value)
      .map((item2: any) => {
        return Object.assign(item2, {
          active: false,
        });
      });
  });

  const negativePromptListWithCategory = JSON.parse(
    JSON.stringify(
      state.promptCategoryList.filter((item1: any) => {
        return (
          negativePromptList.filter(
            (item2: any) => item2.category === item1.value
          ).length > 0
        );
      })
    )
  );
  negativePromptListWithCategory.forEach((item: any) => {
    item.checkAll = false;
    item.content = negativePromptList
      .filter((item2: any) => item2.category === item.value)
      .map((item2: any) => {
        return Object.assign(item2, {
          active: false,
        });
      });
  });

  state.positivePromptListWithCategory = positivePromptListWithCategory;
  state.negativePromptListWithCategory = negativePromptListWithCategory;
  state.loadingFlag = false;

  state.sizePresetListTop = getPresetSizeTop();
  state.sizePresetListBottom = getPresetSizeBottom();

  if (!global.$store.state.app.applySettingsUsed) {
    applySettings();
  } else {
    initCachedSettingData(currentPreviewList.value.length - 1);
  }

  emitPositivePromptString();
  emitNegativePromptString();
  emitOnSettingChanged();
};

const emitOnSettingChanged = () => {
  emit(
    "onSettingChanged",
    Object.assign(state.formData, {
      useNegativePrompt: state.useNegativePrompt,
      numInferenceStepsRefiner: state.formData.numInferenceStepsRefiner,
      useRefiner: state.useRefiner,
      useFp32: state.useFp32,
      useLcmLora: state.useLcmLora,
      sampler: state.sampler,
      setSeed: state.setSeed,
    })
  );
};

const handleChangeUseRefiner = (value: any) => {
  console.log("handleChangeUseRefiner++++", value);
  console.log("handleChangeUseRefiner++++", state.useRefiner);
  emitOnSettingChanged();
};

const checkIfCheckAll = (promptType: string, category: string) => {
  let result: string | boolean = false;
  let promptListByCategoryData = [] as any;
  if (promptType === "positive") {
    promptListByCategoryData = state.positivePromptListWithCategory.find(
      (item: any) => item.value === category
    );
  }

  if (promptType === "negative") {
    promptListByCategoryData = state.negativePromptListWithCategory.find(
      (item: any) => item.value === category
    );
  }

  if (!promptListByCategoryData) return false;

  const promptListByCategory = promptListByCategoryData.content;
  const activePromptList = promptListByCategory.filter(
    (item: any) => item.active
  );

  if (
    activePromptList.length > 0 &&
    activePromptList.length < promptListByCategory.length
  ) {
    result = "intermediate";
  } else {
    result = !(activePromptList.length === 0);
  }

  return result;
};
const getActiveTag = (promptList: any) => {
  if (!promptList) return [];
  return promptList.filter((item: any) => item.active);
};

const handleCloseTag = async (data: any) => {
  // 123
  state.positivePromptListWithCategory.forEach((item1: any) => {
    item1.content.forEach((item2: any) => {
      if (item2.id === data.id) {
        item2.active = false;
      }
    });
  });

  state.negativePromptListWithCategory.forEach((item1: any) => {
    item1.content.forEach((item2: any) => {
      if (item2.id === data.id) {
        item2.active = false;
      }
    });
  });

  emitPositivePromptString();
  emitNegativePromptString();

  $forceUpdate();
};

const transformPromptOptionsToString = () => {
  let positivePromptString = "";
  let negativePromptString = "";

  state.positivePromptListWithCategory.forEach((item: any) => {
    const activeList = getActiveTag(item.content);
    positivePromptString += activeList.map((item2: any) => item2.value.trim());
    if (activeList.length > 0) positivePromptString += ",";
  });
  state.negativePromptListWithCategory.forEach((item: any) => {
    const activeList = getActiveTag(item.content);
    negativePromptString += activeList.map((item2: any) => item2.value.trim());
    if (activeList.length > 0) negativePromptString += ",";
  });
  state.positivePromptString = positivePromptString;
  state.negativePromptString = negativePromptString;
};

const handlePreviewPrompt = () => {
  state.previewPromptVisible = true;
};

const handleClosePreviewDialog = () => {
  state.previewPromptVisible = false;
};

const getModelInfoPromise = () => {
  return new Promise((resolve, reject) => {
    modelManagemenGetRequest()
      .then((response: any) => {
        state.modelInfo = response.data;
        resolve(response);
      })
      .catch((error: any) => {
        console.log(error);
        reject(error);
      });
  });
};

const parseDefaultSettings = () => {
  const defaultSettingsString = state.modelInfo[0].defaultSettings;
  let defaultSettingsObject = {} as any;
  try {
    defaultSettingsObject = JSON.parse(defaultSettingsString);

    if (defaultSettingsObject.useRefiner) {
      state.useRefiner = defaultSettingsObject.useRefiner;
    }

    Object.keys(defaultSettingsObject).forEach((item: string) => {
      state.formData[item] = defaultSettingsObject[item];
    });
  } catch (error) {
    return;
  }
};

const emitPositivePromptString = () => {
  transformPromptOptionsToString();
  emit("onPositivePromptChanged", {
    options: state.positivePromptString,
    custom: state.customPositivePrompt,
  });
};

const emitNegativePromptString = () => {
  transformPromptOptionsToString();
  emit("onNegativePromptChanged", {
    options: state.negativePromptString,
    custom: state.customNegativePrompt,
  });
};

const handleChangeCustomPositivePrompt = () => {
  emitPositivePromptString();
};

const handleChangeCustomNegativePrompt = () => {
  emitNegativePromptString();
};

const handleChooseRatio = (index: number) => {
  state.ratioSettingsDictionary.forEach((item: any, index2: number) => {
    item.active = index === index2;
  });
  state.sizePresetListTop = getPresetSizeTop();
  state.sizePresetListBottom = getPresetSizeBottom();
  emitOnSettingChanged();
};

const checkSizeActive = (size: string) => {
  const width: number = Number(size.split(":")[0]);
  const height: number = Number(size.split(":")[1]);
  const result: boolean =
    state.formData.width === width && state.formData.height === height;
  return result;
};

const handleChooseSize = (size: string) => {
  const width: number = Number(size.split(":")[0]);
  const height: number = Number(size.split(":")[1]);
  state.formData.width = width;
  state.formData.height = height;
  emitOnSettingChanged();
};

const handleChangeCollpase = (value: any) => {
  console.log(value);

  state.useNegativePrompt = !!value.find(
    (item: string) => item === "useNegativePrompt"
  );
  state.useRefiner = !!value.find((item: string) => item === "useRefiner");
  state.setSeed = !!value.find((item: string) => item === "setSeed");
  emit("onChangeUseNegativePrompt", state.useNegativePrompt);
  emitOnSettingChanged();
};

const initCachedSettingData = (index: number) => {
  if (currentPreviewList.value.length === 0) return;
  const chosenPreviewData = currentPreviewList.value[index];
  console.log("=====chosenPreviewData=====");
  console.log(chosenPreviewData);
  const chosenPositivePreviewDataString = chosenPreviewData.positivePrompt;
  const chosenNegativePreviewDataString = chosenPreviewData.negativePrompt;
  const chosenPositivePromptData = chosenPositivePreviewDataString
    ? chosenPositivePreviewDataString.split(",")
    : [];
  const chosenNegativePromptData = chosenNegativePreviewDataString
    ? chosenNegativePreviewDataString.split(",")
    : [];

  state.positivePromptListWithCategory.forEach((item: any, index1: number) => {
    item.content.forEach((item2: any, index2: number) => {
      state.positivePromptListWithCategory[index1].content[index2].active =
        !!chosenPositivePromptData.find((item3: any) => item3 === item2.value);
    });
    item.checkAll = checkIfCheckAll("positive", item.value);
  });
  state.negativePromptListWithCategory.forEach((item: any, index1: number) => {
    item.content.forEach((item2: any, index2: number) => {
      state.negativePromptListWithCategory[index1].content[index2].active =
        !!chosenNegativePromptData.find((item3: any) => item3 === item2.value);
    });
    item.checkAll = checkIfCheckAll("negative", item.value);
  });

  state.positivePromptString = chosenPositivePreviewDataString;
  state.negativePromptString = chosenNegativePreviewDataString;

  console.log(chosenPreviewData);

  state.customNegativePrompt = chosenPreviewData.customNegativePrompt;
  state.customPositivePrompt = chosenPreviewData.customPositivePrompt;

  state.setSeed = global.$isNotEmpty(chosenPreviewData.seed);
  state.formData.seed = chosenPreviewData.seed;
  state.formData.width = chosenPreviewData.width;
  state.formData.height = chosenPreviewData.height;

  state.useNegativePrompt =
    global.$isNotEmpty(chosenPreviewData.customNegativePrompt) ||
    global.$isNotEmpty(chosenNegativePreviewDataString);

  state.useRefiner = chosenPreviewData.useRefiner;

  state.formData.numInferenceSteps = chosenPreviewData.numInferenceSteps;
  state.formData.numInferenceStepsRefiner =
    chosenPreviewData.numInferenceStepsRefiner;
};

const applySettings = async () => {
  const applySettingsData = global.$store.state.app.applySettingsData;
  if (!applySettingsData) return;
  const positivePromptList = applySettingsData.positivePrompt.split(",");
  const negativePromptList = applySettingsData.negativePrompt.split(",");
  console.log("=====applySettingsUsed=====");
  console.log(positivePromptList);
  console.log(state.positivePromptListWithCategory);

  state.positivePromptListWithCategory.forEach(async (item: any) => {
    item.content.forEach((item2: any) => {
      item2.active = !!positivePromptList.find(
        (item3: any) => item3 === item2.value
      );
    });

    item.checkAll = checkIfCheckAll("positive", item.value);
  });
  console.log("positivePromptListWithCategory");
  console.log(state.positivePromptListWithCategory);
  state.negativePromptListWithCategory.forEach((item: any) => {
    item.content.forEach((item2: any) => {
      item2.active = !!negativePromptList.find(
        (item3: any) => item3 === item2.value
      );
    });
    item.checkAll = checkIfCheckAll("negative", item.value);
  });

  state.customPositivePrompt = applySettingsData.customPositivePrompt;
  state.customNegativePrompt = applySettingsData.customNegativePrompt;

  if (
    global.$isNotEmpty(applySettingsData.customNegativePrompt) ||
    global.$isNotEmpty(applySettingsData.negativePrompt)
  ) {
    state.useNegativePrompt = true;
  }

  if (global.$isNotEmpty(applySettingsData.numInferenceStepsRefiner)) {
    state.useRefiner = true;
  }

  if (global.$isNotEmpty(applySettingsData.seed)) {
    state.setSeed = true;
  }

  console.log("applySettingsData+++++");
  console.log(applySettingsData);
  state.formData.width = applySettingsData.width;
  state.formData.height = applySettingsData.height;
  state.formData.numInferenceSteps = applySettingsData.numInferenceSteps;
  state.formData.numInferenceStepsRefiner =
    applySettingsData.numInferenceStepsRefiner || 0;
  state.formData.seed = applySettingsData.seed
    ? Number(applySettingsData.seed)
    : undefined;

  matchRatioSetting(applySettingsData);

  emitPositivePromptString();
  emitNegativePromptString();
  emitOnSettingChanged();
  setTimeout(() => {
    global.$store.commit("app/updateApplySettingsUsed", true);
  }, 2000);

  emit(
    "onSettingChanged",
    Object.assign(state.formData, {
      useNegativePrompt: state.useNegativePrompt,
    })
  );
};

const matchRatioSetting = async (settingData: any) => {
  console.log("matchRatioSetting");
  console.log(state.ratioSettingsDictionary);
  console.log(settingData.width);
  console.log(settingData.height);

  state.ratioSettingsDictionary.forEach((item: any, index: number) => {
    item.sizeList.forEach((item2: any) => {
      const width: number = item2.split(":")[0];
      const height: number = item2.split(":")[1];
      if (
        settingData.width === Number(width) &&
        settingData.height === Number(height)
      ) {
        handleChooseRatio(index);
      }
    });
  });
};

const handleChangeSeed = () => {
  emitOnSettingChanged();
};

const handleChangeUseLcmLora = (value: string | number | boolean) => {
  state.formData.numInferenceSteps = value ? 4 : 30
  emitOnSettingChanged();
}

const handleChangeSampler = (value: string) => {
  emitOnSettingChanged();
}

onMounted(async () => {
  await getModelInfoPromise();
  await getData();
  parseDefaultSettings();
  initData();
  initRandomPromptColor();
  global.$NProgress.done();
});

onBeforeUnmount(() => {
  state.onProgress = false;
});
</script>

<style lang="scss">
.prompt_container {
  display: flex;
  // margin: 1.5rem 0 0 0;
  width: 60%;
  box-sizing: border-box;

  border-right: 1px solid #666;
  text-align: left;
  position: relative;
  font-size: 0;
  overflow: visible;

  .prompt_wrapper {
    min-width: 10rem;
    padding: 0;
    flex: 1;
    border-right: 1px solid #666;

    .el-tabs__header {
      margin-right: 0;
    }

    .el-tabs {
      height: 100%;
      box-sizing: border-box;
    }

    .promitdirectiontabs {
      .el-tabs__header {
        .el-tabs__nav-wrap {
          .el-tabs__nav {
            width: 100%;

            .el-tabs__item {
              flex: 1;
            }
          }
        }
      }

      .el-tabs__content {
        height: calc(100vh - 2.9rem);

        .el-tab-pane {
          height: 100%;

          .el-scrollbar {
            height: 100%;

            .block {
              display: block;
              width: 100%;
              font-size: 0.4rem;

              >h5 {
                display: flex;
                padding: 0.1rem 0.5rem;
                background-color: #ccc;
                color: #000;
                justify-content: space-between;
                align-items: center;
              }

              .content {
                padding: 0.15rem 0;
                display: flex;
                flex-wrap: wrap;

                li {
                  margin: 0.1rem 0.15rem 0.1rem 0.15rem;
                }
              }
            }
          }
        }
      }
    }

    li {
      display: inline-block;
    }
  }

  .setting {
    width: 50%;

    .size_item {
      width: 100%;
    }

    .el-collapse-item__content {
      padding: 0 0 0.2rem 0;
    }

    .settingitem {
      width: 100%;
      align-items: center;
      border-top: 1px solid #444;

      .el-form-item {
        margin-bottom: 0;
        margin: 0.2rem 0;
      }

      .settingitemcontent {
        display: flex;
        width: 100%;

        .switchertitle {
          display: inline-block;
          margin: 0 0.5rem 0 0;
          flex: 1;
          text-align: left;
          font-weight: bold;
        }

        .switcher {
          display: inline-block;
          margin: 0 0.5rem 0 0;
          width: 1.5rem;
          vertical-align: middle;
          text-align: right;
        }

        .select {
          display: inline-block;
          padding: 0 0.5rem 0 0;
          width: 5rem;

          .ant-select {
            width: 100% !important;

          }
        }
      }


    }

    .input_container {
      display: inline-block;
      padding: 0.3rem 0.6rem 0 0.6rem;
      flex: 1;
      width: 100%;
      box-sizing: border-box;

      >.content {
        position: relative;
        margin: 0 0 0.5rem 0;

        // height: 5rem;
        .header {
          width: 50%;
          position: absolute;
          top: 0.1rem;
          right: 0.1rem;

          text-align: right;
          border: 0;
          z-index: 1;

          >span {
            display: inline-block;
            font-size: 0.4rem;
            margin: 0 0.5rem 0 0;
          }

          .previewprompt {
            right: 0;
          }
        }

        .ant-tabs {
          .tablist {
            .ant-tabs-nav-wrap {
              .ant-tabs-nav-list {
                .positiveprompttablabel {
                  .checkbox {
                    margin: 0 0.1rem 0 0;
                    position: relative;
                    top: 0.05rem;
                  }
                }
              }
            }
          }
        }

        .el-textarea {
          background-color: #000;

          .el-textarea__inner {
            box-sizing: border-box;
          }
        }

        .promptarea {
          border: 1px solid #ccc;
          width: 100%;
          min-height: 4rem;
          transition: all 0.3s;
          text-align: left;
          background-color: #fff;
          box-sizing: border-box;

          &:hover {
            border: 1px solid #999;
          }

          ul {
            li {
              display: inline-block;
              margin: 0.1rem;
            }
          }
        }



        .el-collapse-item {
          .el-collapse-item__header {
            .el-form-item {
              width: 100%;

              .el-form-item__content {
                width: 100% !important;


              }
            }
          }
        }

        .userefuner {
          .el-collapse-item__content {
            padding: 0 0 0.5rem 0;
          }
        }
      }

      .el-textarea {
        font-size: 0.5rem;

        :deep(.el-textarea__inner) {
          // padding: 0.2rem 0.4rem;
        }
      }

      .ratiosettings {
        display: flex;
        width: 100%;
        justify-content: space-around;

        li {
          display: flex;
          width: 2rem;
          height: 2rem;
          text-align: center;
          align-items: center;
          justify-content: center;
          cursor: pointer;

          &:hover {
            .outer {
              border: 1px solid #000;
            }
          }

          &.active {
            &:hover {
              .outer {
                border: 1px solid #409eff;
              }
            }

            .outer {
              border: 1px solid #409eff;

              .inner {
                span {
                  &.lefttop {
                    border-color: #409eff transparent transparent #409eff;
                  }

                  &.righttop {
                    border-color: #409eff #409eff transparent transparent;
                  }

                  &.rightbottom {
                    border-color: transparent #409eff #409eff transparent;
                  }

                  &.leftbottom {
                    border-color: transparent transparent #409eff #409eff;
                  }
                }
              }
            }
          }

          .outer {
            display: inline-block;
            padding: 0.1rem;
            border: 1px solid #999;
            transition: all 0.3s;

            .inner {
              display: inline-block;
              width: 100%;
              height: 100%;
              position: relative;

              span {
                display: inline-block;
                width: 10%;
                height: 10%;
                border-style: solid;
                border-width: 1px;
                position: absolute;

                &.lefttop {
                  left: 0;
                  top: 0;
                  border-color: #999 transparent transparent #999;
                }

                &.righttop {
                  right: 0;
                  top: 0;
                  border-color: #999 #999 transparent transparent;
                }

                &.rightbottom {
                  right: 0;
                  bottom: 0;
                  border-color: transparent #999 #999 transparent;
                }

                &.leftbottom {
                  left: 0;
                  bottom: 0;
                  border-color: transparent transparent #999 #999;
                }
              }
            }
          }

          &.onetoone {
            .outer {
              width: 1rem;
              height: 1rem;
            }
          }

          &.tentofifteen {
            .outer {
              width: 0.67rem;
              height: 1rem;
            }
          }

          &.fifteentoten {
            .outer {
              width: 1rem;
              height: 0.67rem;
            }
          }
        }
      }

      .steps {
        margin: 0 0 0.5rem 0;
      }

      .imageratio {
        width: 100%;
        text-align: center;

        ul {
          display: flex;
          width: 100%;
          margin: 0 0 0.2rem 0;
          justify-content: space-between;

          li {
            display: inline-block;

            .a-button {
              width: 3.1rem;
            }
          }
        }
      }
    }
  }

  .previewpromptdialog {
    .content {
      display: flex;
      padding: 0;
      font-size: 0.6rem;
      word-break: break-all;

      .prompt:first-child {
        span {
          padding: 0;
        }
      }

      .prompt {
        display: inline-block;
        flex: 1;

        h5 {
          margin: 0 0 0.5rem 0;
          // text-align: center;
        }

        span {
          display: block;
          // padding: 0 0 0 0.5rem;
          font-size: 0.5rem;
          text-align: center;
          text-align: left;
        }

        p {
          display: block;
          font-size: 0.4rem;
          padding: 0.2rem 0;
        }
      }

      .divider {
        display: inline-block;
        // margin: 0.7rem 0.3rem 0 0.3rem;
        margin: 0 0.5rem;
        width: 1px;
        height: auto;
        min-height: 100%;
        background-color: #666;
      }
    }
  }
}
</style>
