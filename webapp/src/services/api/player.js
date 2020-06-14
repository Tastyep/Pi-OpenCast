import API from "./api";

async function streamMedia(url) {
  return await API.get("player/stream", { params: { url: url } });
}

async function queueMedia(url) {
  return await API.get("player/queue", { params: { url: url } });
}

async function nextMedia() {
  return await API.get("player/next");
}

async function prevMedia() {
  return await API.get("player/prev");
}

async function stopMedia() {
  return await API.get("player/stop");
}

async function pauseMedia() {
  return await API.get("player/pause");
}

async function seekMedia(forward, long) {
  return await API.get("player/seek", {
    params: { forward: forward, long: long },
  });
}

async function updateVolume(value) {
  return await API.get("player/volume", { params: { value: value } });
}

async function toggleSubtitle() {
  return await API.get("player/subtitle/toggle");
}

async function seekSubtitle(forward) {
  return await API.get("player/subtitle/seek", {
    params: { forward: forward },
  });
}

export default {
  streamMedia,
  queueMedia,
  nextMedia,
  prevMedia,
  stopMedia,
  pauseMedia,
  seekMedia,
  updateVolume,
  toggleSubtitle,
  seekSubtitle,
};
