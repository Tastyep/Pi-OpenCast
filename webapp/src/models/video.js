import { action, makeObservable, observable } from "mobx";

export default class Video {
  id = null
  source = ""
  sourceProtocol = ""
  title = ""
  duration = 0
  total_playing_duration = 0
  last_play = null
  collectionId = null
  thumbnail = ""
  location = ""
  streams = {}
  subtitle = ""
  downloadRatio = 0

  constructor(state, eventDispatcher) {
    this.id = state.id;
    this.source = state.source;
    this.sourceProtocol = state.source_protocol;
    this.title = state.title;
    this.duration = state.duration;
    this.total_playing_duration = state.total_playing_duration;
    this.last_play = state.last_play;
    this.collectionId = state.collection_id;
    this.thumbnail = state.thumbnail;
    this.location = state.location;
    this.streams = state.streams;
    this.subtitle = state.subtitle;

    makeObservable(this, {
      downloadRatio: observable,

      _setDownloadRatio: action,
    });

    eventDispatcher.observe(
      { DownloadInfo: (e) => this._setDownloadRatio(e) },
      this.id
    )
  }

  _setDownloadRatio(e) {
    if (e.total_bytes === 0 || e.downloaded_bytes === 0) {
      this.downloadRation = 0
      return
    }
    this.downloadRatio = e.downloaded_bytes / e.total_bytes
  }
}
