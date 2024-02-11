const user = {
  namespaced: true,
  state: {
    baiduAPIAccessInfo: {},
    userInfo: {},
  },
  mutations: {
    updateBaiduAPIAccessInfo: (state: any, payload: object) => {
      state.baiduAPIAccessInfo = payload;
    },
    updateUserInfo: (state: any, payload: object) => {
      state.userInfo = Object.assign(state.userInfo, payload);
    },
  },
  actions: {},
  getters: {},
};

export default user;
