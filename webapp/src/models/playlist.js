import { action, makeObservable, observable } from "mobx"

export default class Playlist {
  constructor(state, eventDispatcher) {
    Object.assign(this, state)
    makeObservable(this, {
      name: observable,
      ids: observable,

      setIds: action,
      rename: action,
    })
    
    eventDispatcher.observe({
      PlaylistContentUpdated: (e) => this.setIds(e.ids),
      PlaylistRenamed: (e) => this.rename(e.name)
    }, this.id)
  }

  setIds(ids) {
    this.ids = ids
  }
  rename(name) {
    this.name = name
  }
}

