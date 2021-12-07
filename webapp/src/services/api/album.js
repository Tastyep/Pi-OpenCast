import { API } from "./api";

async function list() {
  return await API.get("/albums/");
}

async function get(id) {
  return await API.get("/albums/" + id);
}

async function delete_(id) {
  return await API.delete("/albums/" + id);
}

const albumAPI = {
  list,
  get,
  delete_,
};

export default albumAPI;
