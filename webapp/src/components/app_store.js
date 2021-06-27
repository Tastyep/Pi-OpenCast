import { action, makeObservable, observable } from "mobx"

import playerAPI from "services/api/player";
import playlistAPI from "services/api/playlist";
import videoAPI from "services/api/video";

export class AppStore {
  player = {};
  playlists = [];
  videos = [];

  constructor() {
    makeObservable(this, {
      player: observable,
      playlists: observable,
      videos: observable,
      setPlayer: action,
      setPlaylists: action,
      setVideos: action,
      removeVideo: action
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

  setPlayer(player) {
    this.player = player
  }

  setPlaylists(playlists) {
    this.playlists = playlists
  }

  setVideos(videos) {
    this.videos = videos
  }

  playlistVideos(playlistId) {
    let playlist = this.playlists.find(playlist => playlist.id === playlistId)
    return playlist ? this.videos.filter(video => video.id in playlist.ids) : []
  }

 removeVideo(id) {
    this.videos = this.videos.filter(video => video.id !== id)
  }
}

