<template>
  <a-modal
    class="settingdialog_container"
    :open="props.settingVisible"
    @cancel="handleCloseDialog"
    @ok="handleSaveSystenSettings"
    width="15rem"
    title="设置"
  >
    <div class="content">
      <a-form :label-col="{ span: 10 }" :wrapper-col="{ offset: 4 }">
        <a-form-item label="是否带出种子">
          <a-switch v-model:checked="state.ifBringOutSeed" />
        </a-form-item>
        <a-form-item label="深色模式">
          <a-switch v-model:checked="state.darkMode" />
        </a-form-item>
        <a-form-item label="清空暂存区">
          <a-button
            type="primary"
            :loading="state.clearingCache"
            @click="handleClearCache"
          >
            <template #icon><PoweroffOutlined /></template>
            清空
          </a-button>
        </a-form-item>
      </a-form>
    </div>
  </a-modal>
</template>

<script lang="tsx" setup>
import {
  reactive,
  watch,
  computed,
  defineEmits,
  withDefaults,
  defineProps,
  onMounted,
  getCurrentInstance,
  ComponentInternalInstance,
} from "vue";

import { PoweroffOutlined } from "@ant-design/icons-vue";

const currentInstance = getCurrentInstance() as ComponentInternalInstance;
const global = currentInstance.appContext.config.globalProperties;

interface Props {
  settingVisible?: boolean;
  initSettings?: object;
}

const props = withDefaults(defineProps<Props>(), {
  initSettings: {} as any,
  settingVisible: false,
});

const emit = defineEmits(["onCloseDialog", "onConfirmDialog"]);

// const loadingInstance = ElLoading.service();
const state = reactive({
  clearingCache: false,
  ifBringOutSeed: false as boolean,
  darkMode: true as boolean,
  backupSettings: {} as any,
}) as any;
const systemSettings = computed(() => global.$store.state.app.systemSettings);
const currentPreviewList = computed(
  () => global.$store.state.app.currentPreviewList
) as any;

watch(
  () => props.settingVisible,
  async (newValue: any, oldValue: any) => {
    if (newValue) {
      getSystemSettings();
    }
  }
);

// watch(
//   () => systemSettings.value,
//   (newValue: any, oldValue: any) => {
//     triggerDarkMode();
//   }
// );

watch(
  () => props.initSettings,
  (newValue: any, oldValue: any) => {
    console.log("=====watch props.initSettings=====");
    initBackupSettings();
  }
);

const getSystemSettings = () => {
  if (!systemSettings.value || Object.keys(systemSettings.value).length === 0) {
    return;
  }
  assignmentSettingsValue();
};

const assignmentSettingsValue = () => {
  if (props.initSettings instanceof Object) {
    Object.keys(props.initSettings).forEach((item: any) => {
      if (state[item]) {
        state[item] = props.initSettings[item];
      }
    });
  }
};

const handleChangeDarkMode = (value: boolean) => {
  state.systemSettings.darkMode = value;
};

const triggerDarkMode = async () => {
  await nextTick();
  const htmlEl = document.getElementsByTagName("html")[0];
  const mode = systemSettings.value.darkMode;
  htmlEl.setAttribute("class", mode ? "dark" : "");
};

const handleCloseDialog = () => {
  state.systemSettings = state.backupSettings;
  emit("onCloseDialog", false);
};

const handleSaveSystenSettings = () => {
  const systemSettingsDictionary = [
    "clearingCache",
    "ifBringOutSeed",
    "darkMode",
  ];
  let systemSettings = {} as any;
  systemSettingsDictionary.forEach((item: string) => {
    systemSettings[item] = state[item];
  });

  localStorage.setItem("txt2ImgSystemSettings", JSON.stringify(systemSettings));
  global.$store.commit("app/updateSystemSettings", systemSettings);
  global.$message.success("保存成功");

  triggerDarkMode();
  emit("onCloseDialog", false);
  emit("onConfirmDialog", systemSettings);
};

const handleClearCache = () => {
  state.clearingCache = true;
  setTimeout(() => {
    global.$store.commit("app/updateCurrentPreviewList", []);
    sessionStorage.setItem(
      "txt2ImgSessionData",
      JSON.stringify(currentPreviewList.value)
    );
    state.clearingCache = false;
    global.$message.success("清除缓存成功");
  }, 500);
};

const initBackupSettings = async () => {
  await nextTick();
  Object.keys(props.initSettings).forEach((item: string) => {
    state.backupSettings[item] = props.initSettings[item];
  });
  // state.ifBringOutSeed = props.initSettings.ifBringOutSeed;
  // state.darkMode = props.initSettings.darkMode;
  console.log("====state.backupSettings====");
  console.log(state.backupSettings);
};

const restoreSettings = () => {
  state.backupSettings = state.systemSettings;
};

onMounted(async () => {});

onBeforeUnmount(() => {
  restoreSettings();
});
</script>

<style lang="scss">
.settingdialog_container {
  color: #ccc;
  position: relative;
  box-sizing: border-box;

  .content {
    margin: 0 auto;
    position: relative;
    .ant-form {
      margin: 0 auto;
      width: 60%;
    }
  }
}
</style>
