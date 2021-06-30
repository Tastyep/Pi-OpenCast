import { action, makeObservable, observable, computed } from "mobx"

import playerAPI from "services/api/player";
import playlistAPI from "services/api/playlist";
import videoAPI from "services/api/video";

export class AppStore {
  player = {};
  playlists = [];
  videos = [];

  constructor(eventDispatcher) {
    makeObservable(this, {
      player: observable,
      playlists: observable,
      videos: observable,

      setPlayer: action,
      setPlaylists: action,
      setVideos: action,
      removeVideo: action,
      addVideo: action,

      onPlaylistUpdated: action
    })

    eventDispatcher.observe({
      VideoCreated: (e) => this.onVideoCreated(e),
      VideoDeleted: (e) => this.removeVideo(e.model_id),
      PlaylistContentUpdated: (e) => this.onPlaylistUpdated(e), 
    })
  }

  load() {
    this.loadPlayer()
    this.loadVideos()
    this.loadPlaylists()
  }

  loadPlayer() {
    playerAPI
      .get()
      .then((response) => {
        this.setPlayer(response.data)
      })
      .catch((error) => console.log(error)); 
  }
  loadVideos() {
   videoAPI
      .list()
      .then((response) => {
        this.setVideos(response.data.videos)
      })
      .catch((error) => console.log(error)); 
      }
  loadPlaylists() {
   playlistAPI
      .list()
      .then((response) => {
        this.setPlaylists(response.data.playlists)
      })
      .catch((error) => console.log(error));
  }

  onVideoCreated(evt) {
    videoAPI
      .get(evt.model_id)
      .then((response) => {
        this.addVideo(response.data)
      })
      .catch((error) => console.log(error)); 
  }
  
  onPlaylistUpdated(evt) {
    let playlist = this.playlists.find(playlist => playlist.id === evt.model_id)
    if (playlist) {
      playlist.ids = evt.ids
    }
 }

  setPlayer(player) {
    this.player = player
  }

  setPlaylists(playlists) {
    this.playlists = playlists
  }
  playlistVideos(id) {
    return computed(() => {
      const playlist = this.playlists.find(playlist => playlist.id === id)
      if (!playlist) {
        return []
      }
      return this.videos.filter(video => playlist.ids.includes(video.id))
    }).get()
  }

  setVideos(videos) {
    this.videos = videos
  }

  addVideo(video) {
    this.videos.push(video)
  }
  removeVideo(id) {
    this.videos = this.videos.filter(video => video.id !== id)
  }
}
