import API from "./api";

async function list() {
  return await API.get("/videos/");
}

async function get(id) {
  return await API.get("/videos/" + id);
}

async function delete_(id) {
  return await API.delete("/videos/" + id);
}

export default {
  list,
  get,
  delete_,
};
