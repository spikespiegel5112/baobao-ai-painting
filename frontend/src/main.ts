import app from "@/utils/appInstance";

import "normalize.css";
import "element-plus/theme-chalk/el-loading.css";
import "element-plus/theme-chalk/el-message.css";
import "element-plus/theme-chalk/el-notification.css";
import "element-plus/theme-chalk/el-message-box.css";
import "element-plus/theme-chalk/el-drawer.css";

// const HWH5 = require("@/assets/js/hwh5_jsapi.js").default;

app.mount("#app");

import "@/utils/permission.ts";

export default app;
