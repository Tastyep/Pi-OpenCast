class SocketEventDispatcher {
  constructor(websockets) {
    this.eventsToCallbacks = {}
  
    for (const i in websockets) {
      websockets[i].addEventListener('message', (evt) => this.onEvent(evt))
    }
  }

  onEvent(event) {
    const data = JSON.parse(event.data)
    console.log("Received Event", data.name, this.eventsToCallbacks.hasOwnProperty(data.name))
    if (this.eventsToCallbacks.hasOwnProperty(data.name)) {
      const callbacks = this.eventsToCallbacks[data.name] 
      for (const i in callbacks) {
        callbacks[i](data.event)
      }
    }
  }

  observe(eventsToCallback) {
    for (const evt in eventsToCallback) {
      if (this.eventsToCallbacks.hasOwnProperty(evt)) {
        this.eventsToCallbacks[evt].push(eventsToCallback[evt])
      } else {
        this.eventsToCallbacks[evt] = [ eventsToCallback[evt] ]
      }
    }
    console.log("PASS:", this.eventsToCallbacks)
  }
}

export { SocketEventDispatcher }
