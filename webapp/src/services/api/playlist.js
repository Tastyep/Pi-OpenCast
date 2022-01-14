import { API } from "./api";

async function create(data) {
  return await API.post("/playlists/", data);
}

async function list() {
  return await API.get("/playlists/");
}

async function get(id) {
  return await API.get("/playlists/" + id);
}

async function update(id, data) {
  return await API.patch("/playlists/" + id, data);
}

async function delete_(id) {
  return await API.delete("/playlists/" + id);
}

async function videos(playlistId) {
  return await API.get("/playlists/" + playlistId + "/videos");
}

const playlistAPI = {
  create,
  list,
  get,
  update,
  delete_,
  videos,
};

export default playlistAPI;
