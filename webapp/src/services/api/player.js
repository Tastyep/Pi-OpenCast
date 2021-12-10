import { API } from "./api";

async function get() {
  return await API.get("/player/");
}

async function streamMedia(url) {
  return await API.post("/player/stream", null, { params: { url: url } });
}

async function queueMedia(url) {
  return await API.post("/player/queue", null, { params: { url: url } });
}

async function playMedia(id) {
  return await API.post("/player/play", null, {
    params: { id: id },
  });
}

async function stopMedia() {
  return await API.post("/player/stop");
}

async function pauseMedia() {
  return await API.post("/player/pause");
}

async function seekMedia(duration) {
  return await API.post("/player/seek", null, {
    params: { duration: duration },
  });
}

async function updateVolume(value) {
  return await API.post("/player/volume", null, { params: { value: value } });
}

async function toggleSubtitle() {
  return await API.post("/player/subtitle/toggle");
}

async function seekSubtitle(forward) {
  return await API.post("/player/subtitle/seek", null, {
    params: { forward: forward },
  });
}

const playerAPI = {
  get,
  streamMedia,
  queueMedia,
  playMedia,
  stopMedia,
  pauseMedia,
  seekMedia,
  updateVolume,
  toggleSubtitle,
  seekSubtitle,
};

export default playerAPI;
