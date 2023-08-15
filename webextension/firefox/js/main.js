import { STORAGE_KEYS } from "./constant.js";

let storage = browser.storage.local;

async function queryApi(url, data) {
  try {
    const response = await fetch(url, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(data),
    });

    console.log("RESPONSE: ", response);
    return response;
  } catch (error) {
    console.error("Error casting URL:", error);
  }

  return null;
}

function castUrl(url, videoSwitch) {
  const data = {
    dl_opts: {
      download_video: videoSwitch,
      download_subtitles: false,
    },
  };

  storage.get(STORAGE_KEYS.API_IP).then((result) => {
    const apiIp = result[STORAGE_KEYS.API_IP];
    const BASE_URL = `http://${apiIp}/api/player/stream`;
    const reqUrl = `${BASE_URL}?url=${url}`;

    console.log("URL: ", reqUrl);
    queryApi(reqUrl, data);
  });
}

function getActiveTab(handle) {
  // Get the current window
  browser.windows.getCurrent({ populate: true }).then((window) => {
    const activeTab = window.tabs.find((tab) => tab.active);
    if (!activeTab) {
      console.error("No active tab found.");
      return;
    }

    if (!activeTab.url) {
      console.error("Active tab has no URL.");
      return;
    }

    handle(activeTab.url);
  });
}

function redirectUserToWebApp() {
  storage.get(STORAGE_KEYS.WEB_APP_IP).then((result) => {
    const webAppUrl = `http://${result[STORAGE_KEYS.WEB_APP_IP]}`;

    browser.tabs.query({}).then((tabs) => {
      console.log(tabs);
      for (const tab of tabs) {
        console.log(tab);
        if (tab.url.startsWith(webAppUrl)) {
          browser.tabs.update(tab.id, {
            active: true,
          });
          return;
        }
      }
      browser.tabs.create({
        url: webAppUrl,
      });
    });
  });
}

function storeInputUpdates(storageKey, elem, event, handle) {
  elem.addEventListener(event, () => {
    const value = handle();
    storage.set({ [storageKey]: value });
  });
}

document.addEventListener("DOMContentLoaded", function () {
  let externButton = document.getElementById("extern-icon");
  externButton.addEventListener("click", redirectUserToWebApp);

  let videoSwitch = document.getElementById("video-switch");
  storeInputUpdates(STORAGE_KEYS.OPT_CAST_VIDEO, videoSwitch, "click", () => {
    return videoSwitch.checked;
  });

  storage.get(STORAGE_KEYS.OPT_CAST_VIDEO).then((result) => {
    videoSwitch.checked = result[STORAGE_KEYS.OPT_CAST_VIDEO];
  });

  let castButton = document.getElementsByName("cast-button")[0];
  castButton.addEventListener("click", () => {
    getActiveTab((url) => {
      castUrl(url, videoSwitch.checked);
    });
  });
});
