async function handleClick(tab) {
  const data = {
    dl_opts: {
      download_subtitles: false,
      download_video: false,
    },
  };
  const url = `http://192.168.178.74:2020/api/player/stream?url=${tab.url}`;
  console.log("URL: ", url);
  const response = await fetch(url, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(data),
  });

  console.log("RESPONSE: ", response);
}

browser.browserAction.onClicked.addListener(handleClick);
