import axios from "axios";
import RobustWebSocket from "robust-websocket";

// process.env.PORT is undefined for unknown reasons.
const WEBAPP_PORT = process.env.REACT_APP_PORT;
const API_PORT = process.env.REACT_APP_API_PORT;
const API_URL =
  document.location.origin.replace(WEBAPP_PORT, API_PORT) + "/api";
const API = axios.create({
  baseURL: API_URL,
});

const makeWebSocket = (endpoint) => {
  return new RobustWebSocket(API_URL.replace("http", "ws") + endpoint);
};

const listen = () => {
  return makeWebSocket("/events");
};

export { API, API_URL, listen };
