// import "/node_modules/element-plus/es/components/message/style/css";
import { ElMessage } from "element-plus";

/**
 * 安装 按需引入情况下支持 $message方法
 */

const utils = {
  install(app: any, options: object): any {
    const elMessage: any = (op: any) => {
      return ElMessage(op);
    };
    elMessage.success = (op: any) => {
      return ElMessage.success(op);
    };
    elMessage.warning = (op: any) => {
      return ElMessage.warning(op);
    };
    elMessage.error = (op: any) => {
      return ElMessage.error(op);
    };
    elMessage.info = (op: any) => {
      return ElMessage.info(op);
    };

    app.config.globalProperties.$message = elMessage;
  },
} as any;

export default utils;
