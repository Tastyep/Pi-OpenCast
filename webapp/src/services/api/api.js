import axios from "axios";

// process.env.PORT is undefined for unknown reasons.
const API_URL = document.location.origin.replace("8081", "2020") + "/api/";

export default axios.create({
  baseURL: API_URL,
});
