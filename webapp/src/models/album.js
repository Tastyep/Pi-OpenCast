import { action, makeObservable, observable } from "mobx";

export default class Album {
  constructor(state, eventDispatcher) {
    this.id = state.id;
    this.name = state.name;
    this.ids = state.ids;
    this.thumbnail = state.thumbnail;

    makeObservable(this, {
      ids: observable,

      setIds: action,
    });

    eventDispatcher.observe(
      {
        AlbumVideosUpdated: (e) => this.setIds(e.ids),
      },
      this.id
    );
  }

  setIds(ids) {
    this.ids = ids;
  }
}
