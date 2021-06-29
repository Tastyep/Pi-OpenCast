import axios from "axios";
import RobustWebSocket from 'robust-websocket'

// process.env.PORT is undefined for unknown reasons.
const API_URL = document.location.origin.replace("8081", "2020") + "/api";
const API = axios.create({
  baseURL: API_URL,
})

const makeEventListener = (endpoint, eventsToCallback) => {
  let ws = new RobustWebSocket(API_URL.replace("http", "ws") + endpoint)
  ws.addEventListener('message', (event) => {
    const data = JSON.parse(event.data)
    console.log("Received Event", data.name, eventsToCallback.hasOwnProperty(data.name))
    if (eventsToCallback.hasOwnProperty(data.name)) {
      eventsToCallback[data.name](data.event)
    }
  })
}

export {API, API_URL, makeEventListener}
