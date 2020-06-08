import axios from "axios";

const API_URL = "http://localhost:2020/api/";

export default axios.create({
  baseURL: API_URL,
});
