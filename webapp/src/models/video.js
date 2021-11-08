import { action, makeObservable, observable } from "mobx";

// eslint-disable-next-line no-unused-vars
const VideoState = {
  CREATED: "CREATED",
  COLLECTING: "COLLECTING",
  PLAYING: "PLAYING",
  READY: "READY",
};

export default class Video {
  id = null;
  source = "";
  sourceProtocol = "";
  title = "";
  duration = 0;
  totalPlayingDuration = 0;
  lastPlay = null;
  collectionId = null;
  artist = "";
  album = "";
  thumbnail = "";
  location = "";
  streams = {};
  subtitle = "";
  downloadRatio = 0;

  playTime = 0;

  constructor(state, eventDispatcher) {
    this.id = state.id;
    this.source = state.source;
    this.sourceProtocol = state.source_protocol;
    this.title = state.title;
    this.duration = state.duration;
    this.totalPlayingDuration = state.total_playing_duration;
    this.lastPlay = state.last_play;
    this.collectionId = state.collection_id;
    this.artist = state.artist;
    this.album = state.album;
    this.thumbnail = state.thumbnail;
    this.location = state.location;
    this.streams = state.streams;
    this.subtitle = state.subtitle;
    this.state = state.state;

    makeObservable(this, {
      state: observable,
      totalPlayingDuration: observable,
      lastPlay: observable,
      downloadRatio: observable,
      playTime: observable,

      setState: action,
      setTotalPlayingDuration: action,
      setLastPlay: action,

      setPlayTime: action,
      _setDownloadRatio: action,
    });

    eventDispatcher.observe(
      {
        DownloadInfo: (e) => this._setDownloadRatio(e),
        VideoStateUpdated: (e) => {
          this.setState(e.new_state);
          this.setTotalPlayingDuration(e.total_playing_duration);
          this.setLastPlay(e.last_play);
          if (e.new_state === VideoState.PLAYING) {
            this.setPlayTime(0);
          }
        },
      },
      this.id
    );
  }

  setState(state) {
    this.state = state;
  }
  setTotalPlayingDuration(duration) {
    this.totalPlayingDuration = duration;
  }
  setLastPlay(lastPlay) {
    this.lastPlay = lastPlay;
  }
  setPlayTime(playTime) {
    this.playTime = Math.max(0, Math.min(this.duration, playTime));
  }

  _setDownloadRatio(e) {
    if (e.total_bytes === 0 || e.downloaded_bytes === 0) {
      this.downloadRation = 0;
      return;
    }
    this.downloadRatio = e.downloaded_bytes / e.total_bytes;
  }
}
