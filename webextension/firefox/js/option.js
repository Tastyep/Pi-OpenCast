import { STORAGE_KEYS } from "./constant.js";

let storage = browser.storage.local;

function updateIp(key, value) {
  storage
    .set({ [key]: value })
    .then(() => {
      console.log(`${key} set to: ${value}`);
    })
    .catch((error) => {
      console.error("Error setting item:", error);
    });
}

document.addEventListener("DOMContentLoaded", function () {
  let apiIpInput = document.getElementById("api-ip");
  let webappIpInput = document.getElementById("webapp-ip");
  apiIpInput.addEventListener("input", (event) => {
    updateIp(STORAGE_KEYS.API_IP, event.target.value);
  });
  webappIpInput.addEventListener("input", (event) => {
    updateIp(STORAGE_KEYS.WEB_APP_IP, event.target.value);
  });

  storage.get([STORAGE_KEYS.API_IP, STORAGE_KEYS.WEB_APP_IP]).then((result) => {
    apiIpInput.value = result[STORAGE_KEYS.API_IP];
    webappIpInput.value = result[STORAGE_KEYS.WEB_APP_IP];
  });
});
