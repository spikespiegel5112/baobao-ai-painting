// import { getCurrentInstance, ComponentInternalInstance } from "vue";
import service from "@/utils/service";
import { baseURL } from "@/utils/service";

export const userManagementGetRequest = (data: any) => {
  return service({
    url: baseURL + "/user/get/",
    method: "POST",
    data,
  });
};

export const userManagementCreateRequest = (data: any) => {
  return service({
    url: baseURL + "/user/create/",
    method: "POST",
    data,
  });
};

export const userManagementUpdateRequest = (data: any) => {
  return service({
    url: baseURL + "/user/update/",
    method: "POST",
    data,
  });
};

export const userManagementDeleteRequest = (data: any) => {
  return service({
    url: baseURL + "/user/delete/",
    method: "POST",
    data,
  });
};

export const getUserDetailByIdRequest = (data: any) => {
  return service({
    url: baseURL + "/user/getUserDetailById/",
    method: "POST",
    data,
  });
};

export const getUserDetailByAppUserIdRequest = (data: any) => {
  return service({
    url: baseURL + "/user/getUserDetailByAppUserId/",
    method: "POST",
    data,
  });
};

export const getWelinkUserDetailRequest = (data: any) => {
  return service({
    url: baseURL + "/user/getWelinkUserDetail/",
    method: "POST",
    data,
  });
};
