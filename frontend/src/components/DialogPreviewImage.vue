<template>
  <a-modal
    wrapClassName="previewimagedialog_wrapper full-modal"
    v-model:open="state.innerPreviewVisible"
    :closable="false"
    :footer="null"
    width="auto"
    :style="{
      top: '15px',
    }"
  >
    <el-scrollbar :class="{ active: state.innerPreviewVisible }">
      <div class="content" @click.prevent="handleCancel">
        <div class="mask"></div>
        <el-image :src="props.imageUrl" fit="contain" />
      </div>
      <template #footer> </template>
    </el-scrollbar>
  </a-modal>
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

// import AModel from "ant-design-vue/lib/button";
// import "ant-design-vue/lib/button/style";

const currentInstance = getCurrentInstance() as ComponentInternalInstance;
const global = currentInstance.appContext.config.globalProperties;

interface Props {
  previewVisible?: boolean;
  imageUrl?: string;
}

const props = withDefaults(defineProps<Props>(), {
  previewVisible: false,
  imageUrl: "",
});

const emit = defineEmits<{
  (e: "onCloseDialog", data: any): void;
}>();

// const loadingInstance = ElLoading.service();
const state = reactive({
  innerPreviewVisible: false,
});

watch(
  () => global.$router.currentRoute.value,
  (newValue: any, oldValue: any) => {}
);
watch(
  () => props.previewVisible,
  (newValue: any, oldValue: any) => {
    state.innerPreviewVisible = newValue;
  }
);

const handleOk = () => {
  emit("onCloseDialog", false);
};
const handleCancel = () => {
  // state.innerPreviewVisible = false;
  emit("onCloseDialog", false);
};

onMounted(async () => {});

onBeforeUnmount(() => {
  // global.$store.commit("app/updateCurrentPreviewList", []);
  // state.onProgress = false;
});
</script>

<style lang="scss">
.previewimagedialog_wrapper {
  width: 100vw !important;
  height: 100vh;
  flex-direction: column;
  color: #ccc;
  position: relative;
  box-sizing: border-box;
  position: fixed;
  left: 0;
  top: 0;
  background-color: rgba($color: #000000, $alpha: 0.2);

  .ant-modal {
    backdrop-filter: blur(10px);

    .ant-modal-content {
      padding: 0 !important;
      background-color: transparent;

      .ant-modal-body {
        width: 100%;
        // background-color: rgba($color: #000000, $alpha: 0);

        .el-scrollbar {
          width: 100%;
          &.active {
            .el-scrollbar__view {
              .content {
              }
            }
          }
          .el-scrollbar__view {
            width: 100%;
            .content {
              display: flex;
              width: 100%;
              justify-content: center;
              text-align: center;
              align-items: center;
              .el-image {
                display: inline-block;
                height: 96vh;
              }
            }
          }
        }
      }
    }
  }

  .close {
    position: absolute;
    right: -4rem;
    top: 0rem;
    font-size: 1.8rem;
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
