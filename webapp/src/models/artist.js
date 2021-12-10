import { action, makeObservable, observable } from "mobx";

export default class Artist {
  constructor(state, eventDispatcher) {
    this.id = state.id;
    this.name = state.name;
    this.ids = state.ids;
    this.thumbnail = state.thumbnail;

    makeObservable(this, {
      ids: observable,
      thumbnail: observable,

      setIds: action,
      setThumbnail: action,
    });

    eventDispatcher.observe(
      {
        ArtistVideosUpdated: (e) => this.setIds(e.ids),
        ArtistThumbnailUpdated: (e) => this.setThumbnail(e.thumbnail),
      },
      this.id
    );
  }

  setIds(ids) {
    this.ids = ids;
  }

  setThumbnail(thumbnail) {
    this.thumbnail = thumbnail;
  }
}
