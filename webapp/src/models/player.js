import { action, makeObservable, observable } from "mobx"

export default class Player {
  constructor(state, eventDispatcher) {
    Object.assign(this, state)

    makeObservable(this, {
      state: observable,
      sub_state: observable,
      sub_delay: observable,
      video_id: observable,
      volume: observable,

      setState: action,
      setSubState: action,
      setSubDelay: action,
      setVideoId: action,
      setVolume: action,
    })

    eventDispatcher.observe({
      PlayerStarted: (e) => this.onPlayerStarted(e),
      PlayerStopped: (e) => this.onPlayerStopped(e),
      PlayerStateToggled: (e) => this.setState(e.state),
      VolumeUpdated: (e) => this.setVolume(e.volume),
      SubtitleStateUpdated: (e) => this.setSubState(e.state),
      SubtitleDelayUpdated: (e) => this.setSubDelay(e.delay),
    }, this.id)
  }

  onPlayerStarted(e) {
    this.setState("STARTED")
    this.setVideoId(e.video_id)
  }

  onPlayerStopped(_) {
    this.setState("STOPPED")
    this.setVideoId(null)
  }

  setState(state) {
    this.state = state
  }
  setVolume(volume) {
    this.volume = volume
  }
  setSubState(subState) {
    this.sub_state = subState
  }
  setSubDelay(subDelay) {
    this.sub_delay = subDelay
  }
  setVideoId(videoId) {
    this.video_id = videoId
  }
}


