<template>
  <div class="gallery_container">
    <el-scrollbar v-loading="state.loadingFlag">
      <div class="grid">
        <div class="mask" v-if="state.loadingFlag"></div>
        <div
          v-for="(item, index) in state.imageList"
          :key="index"
          class="grid-item"
        >
          <img
            :src="item.url"
            :style="item.style"
            alt=""
            @click="handleOpenPreview"
          />
          <div class="desc"></div>
          <a class="desc" href="javascript:;" @click="handlePreview(item)">
            <el-icon
              class="delete"
              color="#fff"
              @click.stop="handleDeleteImage(item)"
            >
              <Delete />
            </el-icon>
          </a>
        </div>
        <div v-if="state.imageList.length === 0" class="empty">
          <a-empty>
            <template #description>
              <div>空空如也</div>
            </template>
          </a-empty>
        </div>
      </div>
    </el-scrollbar>
    <a-modal
      v-model:open="state.previewDialogVisible"
      title="图片详情"
      @cancel="handleClosePreviewImageDialog"
      width="25rem"
      wrapClassName="preview_wrapper"
    >
      <a-row :gutter="20">
        <a-col class="left" :span="12">
          <el-image
            :src="state.currentImageData.url"
            fit="contain"
            @click="handleOpenPreview"
          />
        </a-col>
        <a-col class="right" :span="12">
          <div class="delete">
            <a-space size="middle">
              <a-switch
                v-model:checked="state.currentImageData.isPublic"
                checked-children="公开"
                un-checked-children="私有"
                size="default"
                @change="handleChangeIsPublic"
                :disabled="state.currentImageData.userId === userInfo.id"
              />
              <a-button
                type="primary"
                danger
                @click.stop="handleDeleteImage(state.currentImageData)"
              >
                <template #icon>
                  <DeleteOutlined />
                </template>
                删除
              </a-button>
            </a-space>
          </div>

          <ul>
            <li>
              <span>正向提示词</span>
              <el-tabs>
                <el-tab-pane label="自定义">
                  <p>
                    {{
                      global.$isNotEmpty(
                        state.currentImageData.customPositivePrompt
                      )
                        ? state.currentImageData.customPositivePrompt
                        : "无"
                    }}
                  </p>
                </el-tab-pane>
                <el-tab-pane label="选项">
                  <p>
                    {{
                      global.$isNotEmpty(state.currentImageData.positivePrompt)
                        ? state.currentImageData.positivePrompt
                        : "无"
                    }}
                  </p>
                </el-tab-pane>
              </el-tabs>
            </li>
            <li>
              <span>反向提示词</span>
              <el-tabs>
                <el-tab-pane label="自定义">
                  <p>
                    {{
                      global.$isNotEmpty(
                        state.currentImageData.customNegativePrompt
                      )
                        ? state.currentImageData.customNegativePrompt
                        : "无"
                    }}
                  </p>
                </el-tab-pane>
                <el-tab-pane label="选项">
                  <p>
                    {{
                      global.$isNotEmpty(state.currentImageData.negativePrompt)
                        ? state.currentImageData.negativePrompt
                        : "无"
                    }}
                  </p>
                </el-tab-pane>
              </el-tabs>
            </li>
            <li>
              <a-row>
                <a-col :span="12">
                  <span>尺寸</span>
                  <div class="size">
                    {{ state.currentImageData.width }} *
                    {{ state.currentImageData.height }}
                  </div>
                </a-col>
                <a-col :span="12">
                  <span>步数</span>
                  <div>
                    {{
                      getOtherSettings(
                        state.currentImageData.otherSettings,
                        "numInferenceSteps"
                      )
                    }}
                  </div>
                </a-col>
              </a-row>
            </li>
            <li>
              <a-row>
                <a-col :span="12">
                  <span>Refiner步数</span>
                  <div>
                    {{
                      getOtherSettings(
                        state.currentImageData.otherSettings,
                        "numInferenceStepsRefiner"
                      ) || "无"
                    }}
                  </div>
                </a-col>
                <a-col :span="12">
                  <span>种子</span>
                  <div>
                    {{ state.currentImageData.seed }}
                  </div>
                </a-col>
              </a-row>
            </li>
          </ul>
        </a-col>
      </a-row>
      <template #footer>
        <a-row justify="end">
          <el-button @click="state.previewDialogVisible = false">
            关闭
          </el-button>
          <el-button type="primary" @click="handleApplyThisSettings">
            采用此参数
          </el-button>
        </a-row>
      </template>
    </a-modal>

    <DialogPreviewImage
      :previewVisible="state.previewVisible"
      :imageUrl="state.currentImageData.url"
      @onCloseDialog="handleClosePreviewImageDialog"
    />
  </div>
</template>

<script lang="tsx" setup>
import {
  reactive,
  watch,
  computed,
  onMounted,
  getCurrentInstance,
  ComponentInternalInstance,
  nextTick,
} from "vue";

import {
  imageManagementGetRequest,
  imageManagementDeleteRequest,
  setImageToPublicRequest,
} from "@/api/image";

import DialogPreviewImage from "@/components/DialogPreviewImage.vue";
import { DeleteOutlined } from "@ant-design/icons-vue";
import Masonry from "masonry-layout";

const currentInstance = getCurrentInstance() as ComponentInternalInstance;
const global = currentInstance.appContext.config.globalProperties;

const state = reactive({
  imageList: [] as any,
  srcArr: [] as any,
  previewDialogVisible: false,
  currentImageData: {} as any,
  loadingFlag: true,
  previewVisible: false,
});

const userInfo = computed(() => {
  return global.$store.state.user.userInfo;
});

const gallaryListCacheData = computed(() => {
  return global.$store.state.app.gallaryListCacheData;
});

const gallaryIsPublic = computed(() => {
  return global.$store.state.app.gallaryIsPublic;
});

watch(
  () => state.imageList,
  (newValue: any, oldValue: any) => {
    getData(null);
  }
);

watch(
  () => gallaryIsPublic.value,
  (newValue: any, oldValue: any) => {
    console.log(newValue);
    state.loadingFlag = true;
    getData(true)
      .then(async (response: any) => {
        await nextTick();
        init(response);
      })
      .catch((error: any) => {});
  }
);

const getData = async (forceUpdate: boolean | null) => {
  return new Promise(async (resolve, reject) => {
    try {
      let imageData = [] as any;
      if (gallaryListCacheData.value.length === 0 || forceUpdate === true) {
        imageData = await getPictureListPromise();
        global.$store.commit("app/updateGallaryListCacheData", imageData);
      } else {
        imageData = gallaryListCacheData.value;
      }

      resolve(imageData);
    } catch (error) {
      reject(error);
    }
  });
};

const handleApplyThisSettings = () => {
  const numInferenceSteps: number = getOtherSettings(
    state.currentImageData.otherSettings,
    "numInferenceSteps"
  );
  const numInferenceStepsRefiner: number = getOtherSettings(
    state.currentImageData.otherSettings,
    "numInferenceStepsRefiner"
  );
  let positivePrompt: string = state.currentImageData.positivePrompt;
  positivePrompt = positivePrompt.substring(0, positivePrompt.lastIndexOf(","));
  let negativePrompt: string = state.currentImageData.negativePrompt;
  negativePrompt = negativePrompt.substring(0, negativePrompt.lastIndexOf(","));
  console.log("handleApplyThisSettings");
  console.log(positivePrompt);
  global.$store.commit("app/updateApplySettingsUsed", false);
  global.$store.commit("app/updateApplySettingsData", {
    customPositivePrompt: state.currentImageData.customPositivePrompt,
    positivePrompt: positivePrompt,
    customNegativePrompt: state.currentImageData.customNegativePrompt,
    negativePrompt: negativePrompt,
    width: state.currentImageData.width,
    height: state.currentImageData.height,
    seed: state.currentImageData.seed,
    numInferenceSteps: numInferenceSteps,
    numInferenceStepsRefiner: numInferenceStepsRefiner,
  });

  console.log("state.currentImageData");
  console.log(state.currentImageData);

  setTimeout(() => {
    global.$router.push({
      name: "Txt2Img",
    });
  }, 500);
};

const handleClosePreviewImageDialog = () => {
  state.previewVisible = false;
  getData(null);
};

const getPictureListPromise: any = () => {
  return new Promise((resolve, reject) => {
    const comesFrom = global.$checkIfWeLink() ? "welink" : "guest";

    imageManagementGetRequest({
      comesFrom: comesFrom,
      // guestUserId: userInfo.value.guestUserId,
      // welinkUserId: userInfo.value.welinkUserId,
      userId: userInfo.value.id,
      isPublic: gallaryIsPublic.value,
    })
      .then((response: any) => {
        response = response.data;

        resolve(response);
      })
      .catch((error: any) => {
        reject(error);
      });
  });
};

const handlePreview = (item: any) => {
  state.previewDialogVisible = true;
  state.currentImageData = item;
};

const init = async (imageData: any[]) => {
  const _baseURL: string = import.meta.env.VITE_BASE_URL;
  const randomData = global.$generateRandom(imageData.length);
  const interval = 1.5 / randomData.length;
  state.imageList = imageData.map((item: any, index: number) => {
    const imageUrl = _baseURL + "/static/" + item.fileName;
    return Object.assign(item, {
      url: imageUrl,
      style: {
        "animation-delay": randomData[index] * interval + 1 + "s",
        "animation-name": "fadeIn",
        "animation-duration": "1s",
        "animation-fill-mode": "forwards",
      },
    });
  });
  // init with selector
  const grid = document.querySelector(".grid");
  setTimeout(() => {
    new Masonry(grid, {
      // set itemSelector so .grid-sizer is not used in layout
      itemSelector: ".grid-item",
      // use element for option
      // columnWidth: "20%",
      // percentPosition: true,
      // horizontalOrder: true,
      // originLeft: true,
      // originTop: true,
    });
    global.$NProgress.done();
    state.loadingFlag = false;
  }, 1000);
};

const handleDeleteImage = (item: any) => {
  global.$confirm("确认删除此图片？", "提示", {}).then(() => {
    confirmDeleteImagePromise(item).then(async () => {
      global.$store.commit("app/cleanGallaryListCacheData");
      state.previewDialogVisible = false;
      getData(null).then((response: any) => {
        init(response);
      });
      global.$message.success("删除成功");
    });
  });
};

const confirmDeleteImagePromise = (item: any) => {
  return new Promise((resolve, reject) => {
    imageManagementDeleteRequest([item.id])
      .then((response: any) => {
        resolve(response);
      })
      .catch((error: any) => {
        reject(error);
      });
  });
};

const getOtherSettings = (data: string, key: string | undefined) => {
  if (!data) return;
  const settingsObject = JSON.parse(data);
  console.log(settingsObject);

  if (key && settingsObject[key]) {
    return settingsObject[key];
  } else {
    return null;
  }
};

const handleOpenPreview = () => {
  state.previewVisible = true;
};

const handleChangeIsPublic = (value: boolean) => {
  setImageToPublicPromise().then(() => {
    global.$message.success(value ? "图片已设为公开" : "图片已设为私有");
    if (gallaryIsPublic.value === true) {
      getData(true).then(async (response: any) => {
        await nextTick();
        init(response);
      });
    }
  });
};

const setImageToPublicPromise = () => {
  return new Promise((resolve, reject) => {
    setImageToPublicRequest({
      id: state.currentImageData.id,
      isPublic: state.currentImageData.isPublic,
    })
      .then((response: any) => {
        resolve(response);
      })
      .catch((error: any) => {
        reject(error);
      });
  });
};

onMounted(async () => {
  getData(null).then(async (response: any) => {
    await nextTick();
    init(response);
  });
});
</script>

<style scoped lang="scss">
.gallery_container {
  width: 100%;
  height: 100vh;
  color: #333;
  position: relative;
  box-sizing: border-box;
  overflow: auto;
  border-right: 1px solid #666;
  z-index: 3;

  .el-scrollbar {
    width: 100%;
    height: calc(100vh - 0rem);
    box-sizing: border-box;
    z-index: 1;
    ul {
      width: 100%;
      height: auto;
    }

    .grid {
      margin: 1.8rem 0 0 0;
      width: 100%;
      font-size: 0;
      .empty {
        margin: 3rem 0 0 0;
        text-align: center;
      }
      .mask {
        width: 100%;
        height: 100%;
        background-color: #000;
        position: absolute;
        top: 0;
        left: 0;
        z-index: 1;
      }

      .grid-sizer {
        width: 20%;
      }
      .grid-item {
        display: inline-block;
        margin: 0 0 1vw 0;
        // padding: 0.3vw;
        width: 20%;
        position: relative;
        font-size: 0;
        text-align: center;
        // border: 2px solid hsla(0, 0%, 0%, 0.5);
        &:hover {
          img {
            border-color: #333;
          }
        }
        img {
          display: inline-block;
          // padding: 0 0.25rem;
          width: 95%;
          height: auto;
          opacity: 0;
          border-width: 1px;
          border-color: transparent;
          border-style: solid;
          transition: all 0.3s;
        }
        .desc {
          width: 100%;
          height: 100%;
          position: absolute;
          top: 0;
          left: 0;
          // background-color: rgba($color: #000000, $alpha: 0.5);
          opacity: 0;
          transition: all 0.3s;
          // border: 2px solid #ccc;
          &:hover {
            opacity: 1;
          }
          .delete {
            position: absolute;
            top: 0.5rem;
            right: 0.5rem;
            font-size: 0.8rem;
            color: #ccc;
            &:hover {
              color: #fff;
            }
          }
        }
      }
    }
  }
}

.preview_wrapper {
  min-width: 20rem !important;
  .left {
    display: inline-block;
    padding: 0 1rem 0 0;
    text-align: center;
    .el-image {
      padding: 0.5rem;
      // border: 1px solid #999;
      height: 80%;
      cursor: zoom-in;
    }
  }
  .right {
    position: relative;
    .delete {
      position: absolute;
      right: 0.4rem;
      top: 0;
    }
    ul {
      margin: 0 0 2rem 0;
      li {
        margin: 0 0 0.5rem 0;
        span {
          display: block;
          margin: 0 0 0.3rem 0;
        }
        p {
          padding: 0.2rem;
          min-height: 2rem;
          line-height: 0.5rem;
          border: 1px solid #666;
        }
      }
    }

    .footer {
      width: 100%;
      text-align: center;
      position: absolute;
      bottom: 0;
      :deep(.a-row) {
        display: block;
        width: 100%;
      }
    }
  }
}
</style>
