import { createApp } from "vue";
import App from "@/App.vue";
import router from "@/router";
import utils from "@/utils/utils";
import elementPlusMessage from "@/utils/elementPlus/elementPlusMessage";
import service from "@/utils/service";

import ElementPlus from "element-plus";
import "element-plus/theme-chalk/src/message.scss";

import * as ElementPlusIconsVue from "@element-plus/icons-vue";

import Antd from "ant-design-vue";
// import "ant-design-vue/dist/antd.css";

const app = createApp(App);

import moment from "moment";
import "moment/locale/zh-cn";
moment.locale("zh-cn");

import { store, key } from "@/store";

import "@/style/element/index.scss";
import "@/style/element/dark.scss";

import "@/style/mobile.scss";
import "@/style/common.scss";
import "@/style/dark.scss";

app.config.globalProperties.$moment = moment;
app.config.globalProperties.$router = router;
app.config.globalProperties.$http = service;

app
  .use(router)
  .use(store, key)
  .use(utils)
  .use(Antd)
  .use(ElementPlus)
  .use(elementPlusMessage);

for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component);
}

export default app;
