import service from "@/utils/service";
import { baseURL } from "@/utils/service";

export const stableDiffusionTxt2ImgBase64DiffuserRequest = (data: any) => {
  return service({
    url: baseURL + "/txt2Img/",
    method: "POST",
    data,
  });
};

export const triggerTxt2ImgByQueueRequest = (data: any) => {
  return service({
    url: baseURL + "/triggerTxt2ImgByQueue/",
    method: "POST",
    data,
  });
};

export const addQueueRequest = (data: any) => {
  return service({
    url: baseURL + "/addQueue/",
    method: "POST",
    data,
  });
};

export const getLastImageDataRequest = () => {
  return service({
    url: baseURL + "/getLastImageData/",
    method: "GET",
  });
};

export const getCancellingProgressRequest = () => {
  return service({
    url: baseURL + "/getCancellingProgress/",
    method: "POST",
  });
};

export const cancelGenerationRequest = () => {
  return service({
    url: baseURL + "/cancelGeneration/",
    method: "POST",
  });
};

export const getGenerationStatusRequest = (data: any) => {
  return service({
    url: baseURL + "/getGenerationStatus/",
    method: "POST",
    data,
  });
};

export const checkQueueByUserIdRequest = (data: any) => {
  return service({
    url: baseURL + "/checkQueueByUserId/",
    method: "POST",
    data,
  });
};

export const deleteQueueRequest = (data: any) => {
  return service({
    url: baseURL + "/deleteQueue/",
    method: "POST",
    data,
  });
};

export const stableDiffusionProgressRequest = () => {
  return service({
    url: baseURL + "/stableDiffusion/progress",
    method: "GET",
  });
};

export const stableDiffusionInternalProgressRequest = () => {
  return service({
    url: baseURL + "/internalProgress",
    method: "POST",
  });
};

export const saveImageToAlbumRequest = (data: any) => {
  return service({
    url: baseURL + "/saveImageToAlbum/",
    method: "POST",
    data,
  });
};

export const promptManagementGetRequest = (data: any) => {
  return service({
    url: baseURL + "/promptManagement/get/",
    method: "POST",
    data,
  });
};

export const dictionaryManagementGetRequest = (data: any) => {
  return service({
    url: baseURL + "/dictionaryManagement/get/",
    method: "POST",
    data,
  });
};

export const promptCategoryManagementGetRequest = (data: any) => {
  return service({
    url: baseURL + "/promptCategoryManagement/get/",
    method: "POST",
    data,
  });
};

export const modelManagemenGetRequest = () => {
  return service({
    url: baseURL + "/modelManagement/get/",
    method: "GET",
  });
};
