import { action, makeObservable, observable, computed } from "mobx";

import playerAPI from "services/api/player";
import playlistAPI from "services/api/playlist";
import videoAPI from "services/api/video";

export class AppStore {
  player = {};
  playlists = {};
  videos = {};
  notifications = [];

  constructor(eventDispatcher, modelFactory) {
    makeObservable(this, {
      player: observable,
      playlists: observable,
      videos: observable,
      notifications: observable,

      setPlayer: action,
      setPlaylists: action,
      setVideos: action,
      insertPlaylistVideo: action,
      removePlaylistVideo: action,

      removeVideo: action,
      addVideo: action,

      addPlaylist: action,
      removePlaylist: action,

      enqueueSnackbar: action,
      removeSnackbar: action,
    });

    this.modelFactory = modelFactory;
    this.eventDispatcher = eventDispatcher;

    eventDispatcher.observe({
      VideoCreated: (e) => this.onVideoCreated(e),
      VideoDeleted: (e) => this.removeVideo(e.model_id),
      PlaylistCreated: (e) => this.onPlaylistCreated(e),
      PlaylistDeleted: (e) => this.removePlaylist(e.model_id),
    });
  }

  load() {
    this.loadPlayer();
    this.loadVideos();
    this.loadPlaylists();
  }

  loadPlayer() {
    playerAPI
      .get()
      .then((response) => {
        this.setPlayer(response.data);
      })
      .catch((error) => console.log(error));
  }
  loadVideos() {
    videoAPI
      .list()
      .then((response) => {
        this.setVideos(response.data.videos);
      })
      .catch((error) => console.log(error));
  }
  loadPlaylists() {
    playlistAPI
      .list()
      .then((response) => {
        this.setPlaylists(response.data.playlists);
      })
      .catch((error) => console.log(error));
  }

  onVideoCreated(evt) {
    videoAPI
      .get(evt.model_id)
      .then((response) => {
        this.addVideo(response.data);
      })
      .catch((error) => console.log(error));
  }

  onPlaylistCreated(evt) {
    playlistAPI
      .get(evt.model_id)
      .then((response) => {
        this.addPlaylist(response.data);
      })
      .catch((error) => console.log(error));
  }

  setPlayer(player) {
    this.player = this.modelFactory.makePlayer(player);
  }

  setPlaylists(playlists) {
    for (const playlist of playlists) {
      this.addPlaylist(playlist);
    }
  }

  addPlaylist(playlist) {
    this.playlists[playlist.id] = this.modelFactory.makePlaylist(playlist);
  }

  removePlaylist(id) {
    delete this.playlists[id];
  }

  insertPlaylistVideo(playlistId, videoId, index) {
    let playlist = this.playlists[playlistId];
    playlist.ids.splice(index, 0, videoId);
  }

  removePlaylistVideo(playlistId, videoId) {
    let playlist = this.playlists[playlistId];
    playlist.ids = playlist.ids.filter((id) => id !== videoId);
  }

  playlistVideos(id) {
    return computed(() => {
      if (!Object.keys(this.playlists).includes(id)) {
        return [];
      }
      const playlist = this.playlists[id];
      let videos = [];
      for (const id of playlist.ids) {
        const video = this.videos[id];
        if (video) {
          videos.push(this.videos[id]);
        }
      }
      return videos;
    }).get();
  }

  setVideos(videos) {
    for (const video of videos) {
      this.addVideo(video);
    }
  }

  addVideo(video) {
    this.videos[video.id] = this.modelFactory.makeVideo(video);
  }
  removeVideo(id) {
    delete this.videos[id];
  }
  playingVideo() {
    if (!this.player.videoId) {
      return null;
    }
    return this.videos[this.player.videoId];
  }

  albums() {
    return computed(() => {
      let albums = {};
      for (const video of Object.values(this.videos)) {
        if (!video.album) {
          continue;
        }
        if (!albums[video.album]) {
          albums[video.album] = {
            videos: [video],
            name: video.album,
          };
        } else {
          albums[video.album].videos.push(video);
        }
      }

      for (const [albumName, album] of Object.entries(albums)) {
        let counts = {};
        let maxCount = 0;

        for (const video of album.videos) {
          counts[video.thumbnail] = (counts[video.thumbnail] || 0) + 1;
          if (counts[video.thumbnail] > maxCount) {
            maxCount = counts[video.thumbnail];
            albums[albumName]["thumbnail"] = video.thumbnail;
          }
        }
      }

      return albums;
    }).get();
  }

  enqueueSnackbar(note) {
    this.notifications.push({
      key: new Date().getTime() + Math.random(),
      ...note,
    });
  }

  removeSnackbar(key) {
    this.notifications = this.notifications.filter(
      (notification) => notification.key !== key
    );
  }
}
