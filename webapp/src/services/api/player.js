import API from "./api";

async function streamMedia(url) {
  return await API.get("player/stream", { params: { url: url } });
}

async function queueMedia(url) {
  return await API.get("player/queue", { params: { url: url } });
}

export default { streamMedia, queueMedia };
