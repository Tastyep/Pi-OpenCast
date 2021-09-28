import axios from "axios";
import RobustWebSocket from "robust-websocket";

// process.env.PORT is undefined for unknown reasons.
const API_URL = document.location.origin.replace("8081", "2020") + "/api";
const API = axios.create({
  baseURL: API_URL,
});

const makeWebSocket = (endpoint) => {
  return new RobustWebSocket(API_URL.replace("http", "ws") + endpoint);
};

const listen = () => {
  return makeWebSocket("/events");
}

export { API, API_URL, listen };
