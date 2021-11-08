import { PlayerState } from "models/player";

class UpdateMediaTime {
  video_id = null;
  task = null;

  constructor(store, eventDispatcher) {
    this.store = store;

    eventDispatcher.observe({
      PlayerStateUpdated: (e) => this.onPlayerStateUpdated(e),
    });
  }

  onPlayerStateUpdated(e) {
    const rps = 3;
    if (e.new_state === PlayerState.PLAYING) {
      this.task = setInterval(() => {
        const videoId = this.store.player.videoId;
        if (!videoId) {
          return;
        }

        let video = this.store.videos[videoId];
        if (!video || video.duration === 0) {
          return;
        }

        const delta = 1 / rps / (video.duration / 100);
        video.setPlayTime(video.playTime + delta);
      }, 1000 / rps);
      return;
    }

    if (!this.task) {
      return;
    }

    clearInterval(this.task);
    this.task = null;
  }
}

export { UpdateMediaTime };
