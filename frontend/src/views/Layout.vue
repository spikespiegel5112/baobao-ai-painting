<template>
  <div class="layout_container" :class="{ mobile: state.mobileMode, welink: global.$checkIfWeLink() }" ref="layoutRef">
    <div class="header">
      <div class="mask"></div>
      <a-row class="content">
        <a-col :span="18">
          <div class="logo">Stable Diffusion XL</div>
          <div class="menu">
            <ul>
              <li v-for="(item, index) in state.menuList" :key="index" :class="{ active: item.active }">
                <a href="javascript:;" @click="handleChooseMenu(item)">
                  {{ item.title }}
                </a>
              </li>
            </ul>
          </div>
        </a-col>
        <a-col :span="6">
          <ul class="settings">
            <li v-if="global.$router.currentRoute.value.name.trim() === 'Gallery'">
              <a href="javascript:;">
                <a-switch v-model:checked="state.isPublic" @change="handleChangeToggleIsPublic"></a-switch>
              </a>
              <span>{{ state.isPublic ? "公开图集" : "私有图集" }}</span>
            </li>
            <el-divider v-if="global.$router.currentRoute.value.name.trim() === 'Gallery'" direction="vertical" />
            <li @click.stop="handleOpenSetting">
              <a href="javascript:;">
                <SettingOutlined />
              </a>
              <span>设置</span>
            </li>

            <li class="avatar">
              <a href="javascript:;">
                <img v-if="welinkUserDetail && welinkUserDetail.avatar" :src="welinkUserDetail.avatar" alt="" />
                <SmileOutlined v-else class="defaultavatar" />
              </a>
              <span class="name">
                {{ welinkUserDetail.userNameCn || "Guest" }}
              </span>
            </li>

            <br />
          </ul>
        </a-col>
      </a-row>
    </div>
    <div class="content" ref="contentRef" v-if="state.pageReady">
      <router-view></router-view>
    </div>
    <div v-else class="backgroundcolor"></div>
    <DialogSettings v-if="Object.keys(systemSettings).length > 0" :settingVisible="state.settingVisible"
      :initSettings="systemSettings" @onCloseDialog="handleCloseSettingDialog"
      @onConfirmDialog="handleConfirmSettingDialog" />
  </div>
</template>

<script lang="tsx" setup>
import VConsole from "vconsole";
import { Moon, Sunny } from "@element-plus/icons-vue";
import { SmileOutlined, SettingOutlined } from "@ant-design/icons-vue";

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

import {
  generateSignatureRequest,
  getHWH5UserIdByAuthCodeRequest,
} from "@/api/auth";

import {
  userManagementCreateRequest,
  userManagementUpdateRequest,
  getUserDetailByIdRequest,
  getUserDetailByAppUserIdRequest,
  getWelinkUserDetailRequest,
} from "@/api/user";

import { v4 as uuidv4 } from "uuid";
import { message } from "ant-design-vue";
const [messageApi, contextHolder] = message.useMessage();

// import Txt2Img from "@/views//Txt2Img/Txt2Img.vue";
// import Gallery from "@/views/Gallery.vue";
import DialogSettings from "@/views/DialogSettings.vue";
import { createSecureServer } from "http2";

const currentInstance = getCurrentInstance() as ComponentInternalInstance;
const global = currentInstance.appContext.config.globalProperties;

const layoutRef = ref(HTMLDivElement);
const contentRef = ref(HTMLDivElement);

const state = reactive({
  clientWidth: 0,
  mobileMode: false,
  isWeLink: false,
  pageReady: false,
  darkMode: true,
  menuList: [
    {
      title: "图集",
      name: "Gallery",
      active: false,
    },
    {
      title: "文生图",
      name: "Txt2Img",
      active: false,
    },
    {
      title: "图生图",
      name: "Img2Img",
      active: false,
    },
  ],
  promptList: [] as any,
  settingVisible: false,
  ifUserExist: false,
  isPublic: false,
});

const contentStyle = computed(() => {
  let result = {
    height: "",
  };

  result.height =
    !!contentRef.value && contentRef.value.clientHeight > window.innerHeight
      ? "100%"
      : "auto";
  return result;
}) as any;

const userInfo = computed(() => {
  return global.$store.state.user.userInfo;
});

const welinkUserDetail = computed(() => {
  return global.$store.state.user.userInfo.welinkUserDetail || {};
});

const systemSettings = computed(() => global.$store.state.app.systemSettings);

const defaultSystemSettings = computed(
  () => global.$store.state.app.defaultSystemSettings
);

watch(
  () => state.pageReady,
  (newValue: any, oldValue: any) => {
    if (!!newValue) {
      hideLoading();
    }
  }
);

watch(
  () => global.$router.currentRoute.value,
  (newValue: any, oldValue: any) => {
    state.menuList.forEach((item: any) => {
      item.active = item.name === newValue.name;
    });
  }
);

watch(
  () => systemSettings.value,
  (newValue: any, oldValue: any) => {
    triggerDarkMode();
  }
);

const _HWH5 = window.HWH5;
const init = () => {
  state.mobileMode = checkMobileMode();
  checkActive();
};

const checkActive = () => {
  state.menuList.forEach((item: any) => {
    item.active = item.name === global.$route.name;
  });
};

const handleChooseMenu = (data: any) => {
  global.$router.push({
    name: data.name,
  });
};

const checkMobileMode = () => {
  state.clientWidth = layoutRef.value.clientWidth;
  return state.clientWidth <= 600;
};

const hideLoading = async () => {
  await nextTick();
  const loop = () => {
    const lineScaleEl = document.getElementById("line-scale") as HTMLElement;
    let count = 0;
    setTimeout(() => {
      if (!lineScaleEl && count < 200) {
        loop();
        count++;
      } else {
        lineScaleEl.style.display = "none";
      }
    }, 200);
  };
  loop();
};

const authHWH5Promise = (_HWH5: any) => {
  return new Promise((resolve, reject) => {
    /* 如果鉴权成功，会执行ready方法，把需要在页面加载时调用的相关接口放在ready中确保执行。
需要用户触发时才调用的接口，则直接调用，不需要放在ready函数中。*/
    generateSignaturePromise()
      .then((response2: any) => {
        response2 = response2.data.result;
        const configParams = {
          appId: response2.clientId, // 应用的client_id
          timestamp: response2.timeStamp, // 与生成签名一致的时间戳，精确到秒十位
          noncestr: response2.nonceStr, // 服务端使用的随机串
          signature: response2.signature, // 签名信息
          jsApiList: ["getUserInfo"],
        };
        console.log("configParams++++++", configParams);
        _HWH5.config(configParams);
        _HWH5.ready((response3: any) => {
          console.log("==========HWH5.ready==========", window);
          resolve(response3);
        });
        // 如果鉴权失败，则调用error方法
        _HWH5.error((error: any) => {
          console.error("鉴权失败---", error);
          message.error(`${error.msg}(${error.errorCode})`);
          reject(error);
        });
      })
      .catch((error) => {
        error = error.data;
        const jsticketsInfo = error.jsticketsInfo;
        if (jsticketsInfo) {
          global.$message.error(
            `${jsticketsInfo.errorMessage}(${jsticketsInfo.errorCode})`
          );
        }

        console.error(error);
        reject(error);
      });
  });
};

const generateSignaturePromise = () => {
  return new Promise((resolve, reject) => {
    const currentUrl = location.origin + location.pathname;
    generateSignatureRequest({
      url: currentUrl,
    })
      .then((response: any) => {
        console.log("generateSignature++++++", response);
        resolve(response);
      })
      .catch((error: any) => {
        console.log("generateSignature error++++", error);
        reject(error);
      });
  });
};

const getHWH5UserIdByAuthCodePromise = async (authCodeData: any) => {
  return new Promise(async (resolve, reject) => {
    try {
      console.log("_HWH5.getAuthCode()++++++", authCodeData);
      const userInfoResponse = await getHWH5UserIdByAuthCodeRequest({
        code: authCodeData.code,
      });

      resolve(userInfoResponse);
    } catch (error) {
      reject(error);
    }
  });
};

const userManagementCreatePromise = () => {
  return new Promise(async (resolve, reject) => {
    // const userDetail = await getUserDetailByAppUserIdRequest({
    //   welinkUserId: userInfo.welinkUserId,
    //   guestUserId: userInfo.guestUserId,
    // });
    const welinkUserDetail: any = userInfo.value.welinkUserDetail;
    let welinkData: object = {};
    if (welinkUserDetail) {
      welinkData = {
        userNameCn: welinkUserDetail.userNameCn,
        userNameEn: welinkUserDetail.userNameEn,
        welinkUserId: userInfo.value.welinkUserId,
        welinkTenantId: userInfo.value.welinkTenantId,
      };
    }

    const params = Object.assign(
      {
        guestUserId: userInfo.value.guestUserId,
      },
      welinkData
    );

    console.log(params);
    userManagementCreateRequest(params)
      .then((response: any) => {
        console.log("userCreateOrUpdateUserInfoRequest+++", response);
        resolve(response);
      })
      .catch((error: any) => {
        console.log(error);
        reject(error);
      });
  });
};

const initHWH5 = async () => {
  state.pageReady = false;
  let userInfoData: any = null;

  // 如果是welink用户
  if (global.$checkIfWeLink()) {
    console.log("==========is Welink==========", _HWH5);
    console.log("location+++++", location);
    await authHWH5Promise(_HWH5);
    const authCodeData = await _HWH5.getAuthCode();
    const userInfoResponse: any = await getHWH5UserIdByAuthCodePromise(
      authCodeData
    );

    const welinkUserDetailResponse: any = await getWelinkUserDetailPromise({
      userId: userInfoResponse.data.userId,
    });
    global.$store.commit(
      "user/updateUserInfo",
      Object.assign({
        welinkUserDetail: welinkUserDetailResponse.data,
        welinkUserId: welinkUserDetailResponse.data.userId,
        welinkTenantId: welinkUserDetailResponse.data.welinkTenantId,
        userComesFrom: "welink",
      })
    );
    userInfoData = await getUserDetailByAppUserIdPromise();

    console.log("=====userInfoData====");
    console.log(userInfoData);

    if (!userInfoData.data.exist) {
      // 如果welink用户不存在
      await userManagementCreatePromise();
      const params = {
        id: userInfoData.data.id,
        settings: defaultSystemSettings.value,
      };
      console.log(userInfo.value);
      await updateUserInfoByIdPromise(params);

      global.$store.commit("user/updateUserInfo", params);
    } else {
      // 如果welink用户不存在
      global.$store.commit("user/updateUserInfo", {
        userComesFrom: "welink",
        id: userInfoData.data.id,
      });
    }
  } else {
    // 如果是访客用户
    let chatSdGuestUserInfo = null;
    const chatSdGuestUserInfoString =
      localStorage.getItem("chatSdGuestUserInfo") || "";
    if (global.$isNotEmpty(chatSdGuestUserInfoString)) {
      chatSdGuestUserInfo = JSON.parse(chatSdGuestUserInfoString);
    } else {
      chatSdGuestUserInfo = Object.assign(userInfo.value, {
        guestUserId: "guest_" + uuidv4(),
        exist: false,
        userComesFrom: "guest",
      });
      localStorage.setItem(
        "chatSdGuestUserInfo",
        JSON.stringify(chatSdGuestUserInfo)
      );
    }
    global.$store.commit("user/updateUserInfo", chatSdGuestUserInfo);

    userInfoData = await getUserDetailByAppUserIdPromise();

    if (!userInfoData.data.exist) {
      // 如果访客用户不存在
      userInfoData = await userManagementCreatePromise();

      console.log(userInfo.value);
      global.$store.commit("user/updateUserInfo", {
        id: userInfoData.data.id,
        settings: defaultSystemSettings.value,
      });

      await updateUserInfoByIdPromise({
        id: userInfoData.data.id,
        settings: defaultSystemSettings.value,
      });
    } else {
      // 如果访客用户存在
      global.$store.commit("user/updateUserInfo", {
        id: userInfoData.data.id,
      });
      await nextTick();
    }
  }

  if (global.$isEmpty(userInfoData.data.settings)) {
    global.$store.commit(
      "app/updateSystemSettings",
      defaultSystemSettings.value
    );
    await updateUserInfoByIdPromise({
      id: userInfoData.data.id,
      settings: defaultSystemSettings.value,
    });
  } else {
    global.$store.commit(
      "app/updateSystemSettings",
      JSON.parse(userInfoData.data.settings)
    );
  }
  state.pageReady = true;
};

const getWelinkUserDetailPromise = (params: any) => {
  return new Promise((resolve, reject) => {
    getWelinkUserDetailRequest(params)
      .then((response: any) => {
        resolve(response);
      })
      .catch((error: any) => {
        reject(error);
      });
  });
};

const getUserDetailByAppUserIdPromise = async () => {
  return new Promise((resolve, reject) => {
    getUserDetailByAppUserIdRequest({
      welinkUserId: userInfo.value.welinkUserId,
      guestUserId: userInfo.value.guestUserId,
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

const updateUserInfoByIdPromise = (params: any) => {
  console.log(params);
  return new Promise((resolve, reject) => {
    userManagementUpdateRequest(params)
      .then((response: any) => {
        resolve(response);
      })
      .catch((error: any) => {
        console.log(error);
        reject(error);
      });
  });
};

const handleOpenSetting = () => {
  state.settingVisible = true;
};

const handleCloseSettingDialog = () => {
  state.settingVisible = false;
};

const handleConfirmSettingDialog = (data: any) => {
  updateUserInfoByIdPromise({
    id: userInfo.value.id,
    settings: data,
  });
};

const triggerDarkMode = async () => {
  await nextTick();
  const htmlEl = document.getElementsByTagName("html")[0];
  const mode = systemSettings.value.darkMode;
  htmlEl.setAttribute("class", mode ? "dark" : "");
};

const handleChangeToggleIsPublic = (value: boolean) => {
  // state.isPublic = value;
  global.$store.commit("app/updateGalarryIsPublic", value);
};

onMounted(async () => {
  init();
  initHWH5();
  triggerDarkMode();
});

onBeforeUnmount(() => { });
</script>

<style lang="scss">
.layout_container {
  // display: flex;
  // flex-direction: column;
  width: 100%;
  height: 100vh;
  // min-height: 100vh;
  align-items: center;
  justify-content: center;
  color: #303030;
  overscroll-behavior: none;
  background-color: #faf9fa;
  transition: all 0.3s;
  overflow: auto;

  >.header {
    width: 100%;
    height: 1.5rem;
    font-size: 0.5rem;
    text-align: left;
    color: #333;
    transition: all 0.3s;
    position: absolute;
    z-index: 4;
    border-bottom: 1px solid #333;

    .content {
      width: 100%;
      height: 100%;
      z-index: 1;
      position: absolute;
      top: 0;

      .ant-col {
        &:before {
          content: "";
          display: inline-block;
          width: 0;
          height: 100%;
          vertical-align: middle;
        }

        .logo {
          display: inline-block;
          padding: 0 0.5rem;
          width: 5rem;
          font-size: 0.5rem;
          vertical-align: middle;
          font-family: "BinancePlex-SemiBold";
        }

        .menu {
          display: inline-block;
          flex: 1;

          ul {
            li {
              display: inline-block;
              margin: 0 0.5rem;
              vertical-align: middle;
              font-size: 0.45rem;

              &.active {
                a {
                  background-color: #999;
                  color: #fff;
                }
              }

              a {
                display: inline-block;
                padding: 0.1rem 0;
                width: 3rem;
                text-align: center;
                text-decoration: none;
                color: #333;
                transition: all 0.3s;
                border-radius: 0.1rem;
                border-width: 1px;
                border-style: solid;
                border-color: transparent;

                &:hover {
                  border-color: #ccc;
                }
              }
            }
          }
        }

        .settings {
          display: inline-block;
          padding: 0 0.5rem 0 0;
          width: 100%;
          text-align: right;
          box-sizing: border-box;
          vertical-align: middle;

          .el-divider {
            display: inline-block;
            height: 1rem;
            vertical-align: middle;
          }

          li {
            display: inline-block;
            margin: 0 0.1em 0 0;
            width: 1.5rem;
            height: 1.5rem;
            text-align: center;
            border: 1px solid transparent;
            vertical-align: middle;

            &:hover {
              a {
                color: #000;
              }

              >span {
                color: #000;
                pointer-events: auto;
              }
            }

            a {
              display: block;
              height: 0.85rem;
              font-size: 0.6rem;
              color: #666;
              transition: all 0.3s;

              .el-icon {
                margin: 0.2rem 0 0 0;
              }
            }

            >span {
              display: block;
              // font-size: 0.4rem;
              color: #666;
            }

            &.avatar {
              img {
                margin: 0.1rem 0 0 0;
                width: 0.8rem;
              }

              .defaultavatar {
                margin: 0.15rem 0 0.1rem 0;
                font-size: 0.6rem;
              }
            }
          }
        }
      }
    }

    .mask {
      display: block;
      width: 100%;
      height: 100%;
      position: absolute;
      top: 0;
      left: 0;

      &:before {
        content: "";
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background-color: rgba($color: #fff, $alpha: 0.5);
        backdrop-filter: blur(5px);
      }
    }
  }

  >.content {
    // display: flex;
    // flex: 1;

    width: 100%;
    max-height: 100%;
    position: relative;
    overflow: hidden;
  }
}
</style>
