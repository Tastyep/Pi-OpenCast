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

async function seekMedia(duration) {
  return await API.get("player/seek", { params: { duration: duration } });
}

async function updateVolume(value) {
  return await API.get("player/volume", { params: { value: value } });
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
};
