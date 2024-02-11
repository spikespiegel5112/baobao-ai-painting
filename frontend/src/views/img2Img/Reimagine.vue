<template>
    <div class="generator_container" ref="generatorContainerRef">
        <div class="chat_container">
            <el-scrollbar>
                <div class="main">
                    <div class="content" v-if="state.readyFlag">
                        111
                    </div>
                </div>
            </el-scrollbar>
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

import Prompt from "./Prompt.vue";
import Preview from "./Preview.vue";

const currentInstance = getCurrentInstance() as ComponentInternalInstance;
const global = currentInstance.appContext.config.globalProperties;

const loading = ref(true);

// const loadingInstance = ElLoading.service();
const state = reactive({
    positivePrompt: "",
    negativePrompt: "",
    customPositivePrompt: "",
    customNegativePrompt: "",
    useNegativePrompt: false,
    setSeed: false,
    useRefiner: false,
    useFp32: false,
    useLcmLora: false,
    sampler: '',
    chosenPreviewIndex: 0,
    promptList: [] as any,
    settings: {} as any,
    readyFlag: false,
    appliedSeed: null as number | null,
});

watch(
    () => global.$router.currentRoute.value,
    (newValue: any, oldValue: any) => { }
);


onMounted(async () => {
});

onBeforeUnmount(() => {
    // state.onProgress = false;
});
</script>
  
<style lang="scss">
.generator_container {
    display: flex;
    flex: 1;
    height: 100vh;
    flex-direction: column;
    color: #ccc;
    position: relative;
    box-sizing: border-box;

    .chat_container {
        width: 100%;
        height: 100%;
        overflow: auto;
        position: relative;
        flex-direction: row;

        .main {
            padding: 1.5rem 0 0 0;
            width: 100%;
            height: 100vh;
            box-sizing: border-box;

            >.content {
                display: flex;
                // padding: 1.5rem 0 0 0;
                height: 100%;
                box-sizing: border-box;
                flex-direction: row;
            }

            >.operation {
                margin: 1rem 0 0 0;
                height: 3rem;
            }
        }
    }
}
</style>
  