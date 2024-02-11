import { createRouter, createWebHashHistory, RouteRecordRaw } from "vue-router";

const routes: Array<RouteRecordRaw> = [
  {
    path: "/",
    name: "Layout",
    redirect: "/Txt2Img",
    component: () =>
      import(/* webpackChunkName: "Layout" */ "../views/Layout.vue"),
    children: [
      {
        path: "/Gallery",
        name: "Gallery",
        component: () =>
          import(
            /* webpackChunkName: "Gallery" */ "../views/Gallery/Gallery.vue"
          ),
      },
      {
        path: "/Txt2Img",
        name: "Txt2Img",
        component: () =>
          import(
            /* webpackChunkName: "Txt2Img" */ "../views/Txt2Img/Txt2Img.vue"
          ),
      },
      {
        path: "/Img2Img",
        name: "Img2Img",
        component: () =>
          import(
            /* webpackChunkName: "Img2Img" */ "../views/Img2Img/Img2Img.vue"
          ),
      },
    ],
  },
];

const router = createRouter({
  history: createWebHashHistory(),
  routes,
});
export default router;
