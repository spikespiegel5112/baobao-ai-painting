const app = {
  namespaced: true,
  state: () => ({
    currentPreviewList: [] as any,
    promptListCacheData: [] as any,
    promptCategoryListCacheData: [] as any,
    justRefreshedFlag: true,
    currentSessionId: "",
    applySettingsUsed: false,
    applySettingsData: null,
    gallaryListCacheData: [] as any,
    darkMode: true,
    systemSettings: {} as object,
    defaultSystemSettings: {
      ifBringOutSeed: false as boolean,
      darkMode: true as boolean,
    },
    tagTypeDictionary: [
      "",
      "processing",
      "success",
      "error",
      "warning",
      "magenta",
      "red",
      "volcano",
      "orange",
      "gold",
      "lime",
      "green",
      "cyan",
      "blue",
      "geekblue",
      "purple",
    ],
    gallaryIsPublic: false,
  }),
  mutations: {
    updateDarkMode: (state: any, payload: object) => {
      state.darkMode = payload;
    },
    updateCurrentPreviewList: (state: any, payload: object) => {
      state.currentPreviewList = payload;
    },
    removePreviewByIndex: (state: any, payload: number) => {
      state.currentPreviewList = state.currentPreviewList.filter(
        (item: any, index: number) => index !== payload
      );
    },
    updateJustRefreshedFlag: (state: any, payload: number) => {
      state.justRefreshedFlag = payload;
    },
    updateMobileMode: (state: any, payload: number) => {},
    updateCurrentSessionId: (state: any, payload: number) => {
      state.currentSessionId = payload;
    },
    updateApplySettingsData: (state: any, payload: any) => {
      state.applySettingsData = payload;
    },
    updateApplySettingsUsed: (state: any, payload: boolean) => {
      state.applySettingsUsed = payload;
    },
    updatePromptListCacheData: (state: any, payload: boolean) => {
      state.promptListCacheData = payload;
    },
    updatePromptCategoryListCacheData: (state: any, payload: boolean) => {
      state.promptCategoryListCacheData = payload;
    },
    updateGallaryListCacheData: (state: any, payload: boolean) => {
      state.gallaryListCacheData = payload;
    },
    cleanGallaryListCacheData: (state: any, payload: boolean) => {
      state.gallaryListCacheData = [];
    },
    updateSystemSettings: (state: any, payload: boolean) => {
      state.systemSettings = payload;
    },
    updateGalarryIsPublic: (state: any, payload: boolean) => {
      state.gallaryIsPublic = payload;
    },
  },
  actions: {},
  getters: {},
};

export default app;
