import { action, makeObservable, observable, computed } from "mobx";

const PlayerState = {
  PLAYING: "PLAYING",
  PAUSED: "PAUSED",
  STOPPED: "STOPPED",
};

export default class Player {
  constructor(state, eventDispatcher) {
    this.id = state.id;
    this.queue = state.queue;
    this.state = state.state;
    this.videoId = state.video_id;
    this.subState = state.sub_state;
    this.subDelay = state.sub_delay;
    this.volume = state.volume;

    makeObservable(this, {
      queue: observable,
      state: observable,
      subState: observable,
      subDelay: observable,
      videoId: observable,
      volume: observable,

      setQueue: action,
      setState: action,
      setSubState: action,
      setSubDelay: action,
      setVideoId: action,
      setVolume: action,

      isPlaying: computed,
    });

    eventDispatcher.observe(
      {
        PlayerQueueUpdated: (e) => this.setQueue(e.queue),
        PlayerStateUpdated: (e) => this.onPlayerStateUpdated(e),
        VolumeUpdated: (e) => this.setVolume(e.volume),
        SubtitleStateUpdated: (e) => this.setSubState(e.state),
        SubtitleDelayUpdated: (e) => this.setSubDelay(e.delay),
      },
      this.id
    );
  }

  onPlayerStateUpdated(e) {
    this.setState(e.new);
    this.setVideoId(e.video_id);
  }
  setQueue(playlist_id) {
    this.queue = playlist_id;
  }
  setState(state) {
    this.state = state;
  }
  setVolume(volume) {
    this.volume = volume;
  }
  setSubState(subState) {
    this.subState = subState;
  }
  setSubDelay(subDelay) {
    this.subDelay = subDelay;
  }
  setVideoId(videoId) {
    this.videoId = videoId;
  }

  get isPlaying() {
    return this.state === PlayerState.PLAYING;
  }
}
