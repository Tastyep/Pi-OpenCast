import { STORAGE_KEYS, API_IP, WEB_APP_IP } from "./constant.js";

let storage = browser.storage.local;

function loadStorageDefault() {
  storage.set({
    [STORAGE_KEYS.API_IP]: API_IP,
    [STORAGE_KEYS.WEB_APP_IP]: WEB_APP_IP,
  });
}

loadStorageDefault();
