import router from "@/router";
// import { store } from "@/store";
// import { mapGetters, useStore } from "vuex";
import { utils } from "./utils";

router.beforeEach((to: any, from: any, next: any) => {
  utils.$NProgress.start();
  next();
});

router.afterEach((to, from) => {});

router.onError((error) => {
  console.log("router.onError", error);
  utils.$NProgress.done();
});
