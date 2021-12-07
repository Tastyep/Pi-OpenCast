import { API } from "./api";

async function list() {
  return await API.get("/artists/");
}

async function get(id) {
  return await API.get("/artists/" + id);
}

async function delete_(id) {
  return await API.delete("/artists/" + id);
}

const artistAPI = {
  list,
  get,
  delete_,
};

export default artistAPI;
