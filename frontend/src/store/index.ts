import { createStore, Store } from "vuex";
import { InjectionKey } from "vue";
import app from "./modules/app";
import user from "./modules/user";
import dictionary from "./modules/dictionary";

export interface State {
  app: {
    currentChatTitle: string;
    currentChatDialogNumber: number;
    currentChatList: any;
  };
  user: {
    baiduAPIAccessInfo: any;
    userInfo: any;
  };
}

export const key: InjectionKey<Store<State>> = Symbol();

export const store = createStore<State>({
  modules: {
    app,
    user,
    dictionary,
  } as any,
});
