
import { API, makeEventListener } from "./api";

async function list() {
  return await API.get("/videos/");
}

async function get(id) {
  return await API.get("/videos/" + id);
}

async function delete_(id) {
  return await API.delete("/videos/" + id);
}

function listen(eventsToCallback) {
  return makeEventListener("/videos/events", eventsToCallback)
}

export default {
  list,
  get,
  delete_,
  listen,
};
