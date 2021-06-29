class SocketEventDispatcher {
  constructor(websockets) {
    this.eventsToCallbacks = new Map()
  
    for (const i in websockets) {
      websockets[i].addEventListener('message', (evt) => this.onEvent(evt))
    }
  }

  onEvent(event) {
    const data = JSON.parse(event.data)
    console.log("Received Event", data.name, this.eventsToCallbacks.has(data.name))
    if (this.eventsToCallbacks.has(data.name)) {
      const callbacks = this.eventsToCallback[data.name] 
      for (const i in callbacks) {
        callbacks[i](data.event)
      }
    }
  }

  observe(eventsToCallback) {
    for (const evt in eventsToCallback) {
      if (this.eventsToCallbacks.has(evt)) {
        this.eventsToCallbacks[evt].push(eventsToCallback[evt])
      } else {
        this.eventsToCallbacks[evt] = [ eventsToCallback[evt] ]
      }
    }
  }
}

export { SocketEventDispatcher }
