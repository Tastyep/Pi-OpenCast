class SocketEventDispatcher {
  constructor(websockets) {
    this.eventsToHandlers = {};

    for (const i in websockets) {
      websockets[i].addEventListener("message", (evt) => this.onEvent(evt));
    }
  }

  onEvent(event) {
    const data = JSON.parse(event.data);
    console.log(
      "Received Event",
      data.name,
      this.eventsToHandlers.hasOwnProperty(data.name),
      event.data
    );
    if (this.eventsToHandlers.hasOwnProperty(data.name)) {
      const handlers = this.eventsToHandlers[data.name];
      for (const handler of handlers) {
        if (!handler.modelId || data.event.model_id === handler.modelId) {
          handler.func(data.event);
        }
      }
    }
  }

  observe(eventsToHandler, modelId) {
    for (const evt in eventsToHandler) {
      if (this.eventsToHandlers.hasOwnProperty(evt)) {
        this.eventsToHandlers[evt].push({
          modelId: modelId,
          func: eventsToHandler[evt],
        });
      } else {
        this.eventsToHandlers[evt] = [
          { modelId: modelId, func: eventsToHandler[evt] },
        ];
      }
    }
  }
}

export { SocketEventDispatcher };
