import API from "./api";

async function list() {
  return await API.get("/video/");
}

async function get(id) {
  return await API.get("/video/" + id);
}

async function delete_(id) {
  return await API.delete("/video/" + id);
}

export default {
  list,
  get,
  delete_,
};
