import service from "@/utils/service";
import { baseURL } from "@/utils/service";

export const imageManagementGetRequest = (data: any) => {
  return service({
    url: baseURL + "/imageManagement/get/",
    method: "POST",
    data,
  });
};

export const imageManagementDeleteRequest = (data: any) => {
  return service({
    url: baseURL + "/imageManagement/delete/",
    method: "POST",
    data,
  });
};

export const setImageToPublicRequest = (data: any) => {
  return service({
    url: baseURL + "/imageManagement/setImageToPublic/",
    method: "POST",
    data,
  });
};
