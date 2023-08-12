import { STORAGE_KEYS, API_IP } from "./constant.js";

let storage = browser.storage.local;
storage.set({ [STORAGE_KEYS.API_IP]: API_IP });

function updateApiIp() {
  storage
    .set({ [STORAGE_KEYS.API_IP]: this.value })
    .then(() => {
      console.log("API IP set to: ", this.value);
    })
    .catch((error) => {
      console.error("Error setting item:", error);
    });
}

document.addEventListener("DOMContentLoaded", function () {
  let ipInput = document.getElementsByName("ip-input")[0];
  ipInput.addEventListener("input", updateApiIp);

  storage.get(STORAGE_KEYS.API_IP).then((result) => {
    ipInput.value = result[STORAGE_KEYS.API_IP];
  });
});
