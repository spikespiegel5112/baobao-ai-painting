import service from "@/utils/service";
import { baseURL } from "@/utils/service";

export const dictionaryManagementGetRequest = (data: any) => {
  return service({
    url: baseURL + "/dictionaryManagement/get/",
    method: "POST",
    data,
  });
};
