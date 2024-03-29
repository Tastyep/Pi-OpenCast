import { PlayerState } from "models/player";

class UpdateMediaTime {
  RPS = 3;
  video_id = null;
  task = null;

  constructor(store, eventDispatcher) {
    this.store = store;

    eventDispatcher.observe({
      WSResponse: (e) => this.onWSResponse(e),
      PlayerStateUpdated: (e) => this.onPlayerStateUpdated(e),
      VideoSeeked: (e) => this.onVideoSeeked(e),
    });
  }

  onWSResponse(evt) {
    switch (evt.code) {
      case "play_time":
        let activeVideo = this.store.videos[this.store.player.videoId];
        if (evt.content.play_time < 0 || !activeVideo) {
          return;
        }

        activeVideo.setPlayTime(evt.content.play_time);
        if (!this.task && this.store.player.isPlaying) {
          this._startTask();
        }

        break;
      default:
        console.log("Unhandled websocket message", evt.code);
    }
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

    video.setPlayTime(e.duration);
    if (!this.task && this.store.player.isPlaying) {
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

      video.setPlayTime(video.playTime + 1000 / this.RPS);
    }, 1000 / this.RPS);
  }
}

export { UpdateMediaTime };
