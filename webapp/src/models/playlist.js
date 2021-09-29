import { action, makeObservable, observable } from "mobx";

export default class Playlist {
  constructor(state, eventDispatcher) {
    this.id = state.id;
    this.name = state.name;
    this.ids = state.ids;
    this.generated = state.generated;

    makeObservable(this, {
      name: observable,
      ids: observable,

      setIds: action,
      rename: action,
    });

    eventDispatcher.observe(
      {
        PlaylistContentUpdated: (e) => this.setIds(e.ids),
        PlaylistRenamed: (e) => this.rename(e.name),
      },
      this.id
    );
  }

  setIds(ids) {
    this.ids = ids;
  }
  rename(name) {
    this.name = name;
  }
}
