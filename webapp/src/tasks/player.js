import { PlayerState } from "models/player";

class UpdateMediaTime {
  RPS = 3;
  video_id = null;
  task = null;

  constructor(store, eventDispatcher) {
    this.store = store;

    eventDispatcher.observe({
      PlayerStateUpdated: (e) => this.onPlayerStateUpdated(e),
      VideoSeeked: (e) => this.onVideoSeeked(e),
    });
  }

  onPlayerStateUpdated(e) {
    if (e.new_state === PlayerState.PLAYING) {
      this._startTask();
      return;
    }

    if (!this.task) {
      return;
    }

    clearInterval(this.task);
    this.task = null;
  }

  onVideoSeeked(e) {
    const videoId = this.store.player.videoId;
    if (!videoId) {
      return;
    }

    let video = this.store.videos[videoId];
    if (!video) {
      return;
    }

    video.setPlayTime(e.duration / 1000);
    if (!this.task) {
      this._startTask();
    }
  }

  _startTask() {
    this.task = setInterval(() => {
      const videoId = this.store.player.videoId;
      if (!videoId) {
        return;
      }

      let video = this.store.videos[videoId];
      if (!video || video.duration === 0) {
        return;
      }

      video.setPlayTime(video.playTime + 1 / this.RPS);
    }, 1000 / this.RPS);
  }
}

export { UpdateMediaTime };
