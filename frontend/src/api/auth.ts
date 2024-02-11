import service from "@/utils/service";
import { baseURL } from "@/utils/service";

export const generateSignatureRequest = (data: any) => {
  return service({
    url: baseURL + "/auth/generateSignature/",
    method: "POST",
    data,
  });
};

export const getHWH5UserIdByAuthCodeRequest = (data: any) => {
  return service({
    url: baseURL + "/auth/getHWH5UserIdByAuthCode/",
    method: "POST",
    data,
  });
};
