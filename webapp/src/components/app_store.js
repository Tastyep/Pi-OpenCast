import { action, makeObservable, observable, computed } from "mobx";

import playerAPI from "services/api/player";
import playlistAPI from "services/api/playlist";
import videoAPI from "services/api/video";
import albumAPI from "services/api/album";
import snackBarHandler from "services/api/error";
import { UpdateMediaTime } from "tasks/player";

import SnackMessage from "components/snack_message";

let tasks = [];

export class AppStore {
  player = {};
  playlists = {};
  videos = {};
  albums = {};
  notifications = [];

  constructor(eventDispatcher, modelFactory) {
    makeObservable(this, {
      player: observable,
      playlists: observable,
      videos: observable,
      albums: observable,
      notifications: observable,

      setPlayer: action,
      setPlaylists: action,
      setVideos: action,
      setAlbums: action,
      insertPlaylistVideo: action,
      removePlaylistVideo: action,

      removeVideo: action,
      addVideo: action,

      addPlaylist: action,
      removePlaylist: action,

      addAlbum: action,
      removeAlbum: action,

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
      AlbumCreated: (e) => this.onAlbumCreated(e),
      AlbumDeleted: (e) => this.removeAlbum(e.model_id),
      Notification: (e) =>
        this.enqueueSnackbar(
          {
            message: e.message,
            options: {
              variant: e.level.toLowerCase(),
            },
          },
          e.details
        ),
    });

    tasks.push(new UpdateMediaTime(this, eventDispatcher));
  }

  load() {
    this.loadPlayer();
    this.loadVideos();
    this.loadPlaylists();
    this.loadAlbums();
  }

  loadPlayer() {
    playerAPI
      .get()
      .then((response) => {
        this.setPlayer(response.data);
      })
      .catch(snackBarHandler(this));
  }
  loadVideos() {
    videoAPI
      .list()
      .then((response) => {
        this.setVideos(response.data.videos);
      })
      .catch(snackBarHandler(this));
  }
  loadPlaylists() {
    playlistAPI
      .list()
      .then((response) => {
        this.setPlaylists(response.data.playlists);
      })
      .catch(snackBarHandler(this));
  }
  loadAlbums() {
    albumAPI
      .list()
      .then((response) => {
        this.setAlbums(response.data.albums);
      })
      .catch(snackBarHandler(this));
  }

  onVideoCreated(evt) {
    videoAPI
      .get(evt.model_id)
      .then((response) => {
        this.addVideo(response.data);
      })
      .catch(snackBarHandler(this));
  }

  onPlaylistCreated(evt) {
    playlistAPI
      .get(evt.model_id)
      .then((response) => {
        this.addPlaylist(response.data);
      })
      .catch(snackBarHandler(this));
  }

  onAlbumCreated(evt) {
    albumAPI
      .get(evt.model_id)
      .then((response) => {
        this.addAlbum(response.data);
      })
      .catch(snackBarHandler(this));
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

  get playerPlaylist() {
    return this.playlists[this.player.queue];
  }

  filterVideos(ids) {
    let videos = [];
    for (const id of ids) {
      const video = this.videos[id];
      if (video) {
        videos.push(this.videos[id]);
      }
    }
    return videos;
  }

  playlistVideos(id) {
    return computed(() => {
      if (!Object.keys(this.playlists).includes(id)) {
        return [];
      }
      const playlist = this.playlists[id];
      return this.filterVideos(playlist.ids);
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

  setAlbums(albums) {
    for (const album of albums) {
      this.addAlbum(album);
    }
  }
  addAlbum(album) {
    this.albums[album.id] = this.modelFactory.makeAlbum(album);
  }
  removeAlbum(id) {
    delete this.albums[id];
  }

  artists() {
    return computed(() => {
      let artists = {};
      for (const video of Object.values(this.videos)) {
        if (!video.artist) {
          continue;
        }
        if (!artists[video.artist]) {
          artists[video.artist] = {
            videos: [video],
            name: video.artist,
          };
        } else {
          artists[video.artist].videos.push(video);
        }
      }

      for (let artist of Object.values(artists)) {
        let albums = {};

        for (const video of artist.videos) {
          if (!video.album) {
            continue;
          }
          if (!albums[video.album]) {
            albums[video.album] = {
              name: video.album,
              thumbnails: { [video.thumbnail]: 1 },
              count: 1,
            };
          } else {
            let thumbnail_count =
              albums[video.album].thumbnails[video.thumbnail];
            albums[video.album].thumbnails[video.thumbnail] =
              (thumbnail_count || 0) + 1;
            albums[video.album].count += 1;
          }
        }

        albums = Object.values(albums).sort((a, b) => b.count - a.count);
        for (let album of albums) {
          delete album.count;
          // Sort by count, take the thumbnail of the most found
          album.thumbnail = Object.keys(album.thumbnails).sort(
            (a, b) => album.thumbnails[b] - album.thumbnails[a]
          )[0];
          delete album.thumbnails;
        }

        artist.albums = albums;
      }

      return artists;
    }).get();
  }

  enqueueSnackbar(note, details) {
    note.message = note.message.charAt(0).toUpperCase() + note.message.slice(1);
    if (!note.options.content) {
      note.options.content = (key) => {
        return (
          <SnackMessage
            key={key}
            message={note.message}
            options={note.options}
            details={details}
          />
        );
      };
    }
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
