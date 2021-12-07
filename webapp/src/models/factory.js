import Playlist from "./playlist";
import Video from "./video";
import Player from "./player";
import Album from "./album";
import Artist from "./artist";

export default class ModelFactory {
  constructor(eventDispatcher) {
    this.eventDispatcher = eventDispatcher;
  }

  makeVideo(state) {
    return new Video(state, this.eventDispatcher);
  }
  makePlaylist(state) {
    return new Playlist(state, this.eventDispatcher);
  }
  makePlayer(state) {
    return new Player(state, this.eventDispatcher);
  }
  makeAlbum(state) {
    return new Album(state, this.eventDispatcher);
  }
  makeArtist(state) {
    return new Artist(state, this.eventDispatcher);
  }
}
