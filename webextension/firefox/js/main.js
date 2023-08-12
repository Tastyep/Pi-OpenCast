import { STORAGE_KEYS } from "./constant.js";

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

function castUrl(url) {
  const data = {
    dl_opts: {
      download_subtitles: false,
      download_video: false,
    },
  };

  browser.storage.local.get(STORAGE_KEYS.API_IP).then((result) => {
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
    // Check if there is an active tab
    const activeTab = window.tabs.find((tab) => tab.active);
    if (!activeTab) {
      console.error("No active tab found.");
      return;
    }
    // Check if the active tab has a URL
    if (!activeTab.url) {
      console.error("Active tab has no URL.");
      return;
    }
    // Log the URL to the console (for testing purposes)
    handle(activeTab.url);
  });
}

function toggleButton(button) {
  button.classList.toggle("active");
  console.log("togglw");
}

document.addEventListener("DOMContentLoaded", function () {
  let audioButton = document.getElementById("audio-button");
  let videoButton = document.getElementById("video-button");
  [audioButton, videoButton].forEach((button) => {
    button.addEventListener("click", function () {
      toggleButton(button);
    });
  });

  let castButton = document.getElementsByName("cast-button")[0];
  castButton.addEventListener("click", () => {
    getActiveTab((url) => {
      castUrl(url);
    });
  });
});
