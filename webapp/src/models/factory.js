import Playlist from './playlist'
import Video from './video'
import Player from './player'

export default class ModelFactory {
  constructor(eventDispatcher) {
    this.eventDispatcher = eventDispatcher
  }

  makeVideo(state) {
    return new Video(state, this.eventDispatcher)
  }
  makePlaylist(state) {
    return new Playlist(state, this.eventDispatcher)
  }
  makePlayer(state) {
    return new Player(state, this.eventDispatcher)
  }
}
