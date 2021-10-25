import { useState } from "react";

import {
  Avatar,
  Button,
  Divider,
  IconButton,
  Grid,
  Link,
  ListItem,
  ListItemAvatar,
  ListItemIcon,
  ListItemText,
  Menu,
  MenuItem,
  Paper,
  Stack,
  Typography,
} from "@mui/material";
import MoreVertIcon from "@mui/icons-material/MoreVert";
import PlaylistPlayIcon from "@mui/icons-material/PlaylistPlay";
import PlaylistAddIcon from "@mui/icons-material/PlaylistAdd";
import DeleteOutlineIcon from "@mui/icons-material/DeleteOutline";
import AddIcon from "@mui/icons-material/Add";

import Popper from "@mui/material/Popper";
import ClickAwayListener from "@mui/material/ClickAwayListener";
import MenuList from "@mui/material/MenuList";

import MediaQuery from "react-responsive";
import { SIZES } from "constants.js";

import { durationToHMS } from "services/duration";
import { queueNext } from "services/playlist";
import playlistAPI from "services/api/playlist";
import playerAPI from "services/api/player";
import videoAPI from "services/api/video";
import snackBarHandler from "services/api/error";

import { useAppStore } from "components/app_context";

import PlaylistThumbnail from "components/playlist_thumbnail";
import PlaylistModal from "components/playlist_modal";

const renderArtistAlbum = (video) => {
  const artist = video.artist ? (
    <Link href={`/artists/${video.artist}`} color="inherit" underline="none">
      {video.artist}
    </Link>
  ) : (
    "Artist"
  );

  const album = video.album ? (
    <Link href={`/albums/${video.album}`} color="inherit" underline="none">
      {video.album}
    </Link>
  ) : (
    "Album"
  );

  return (
    <>
      {artist} • {album}
    </>
  );
};

const PlaylistMenu = (props) => {
  const store = useAppStore();

  const { open, anchorEl, video, closeMenu, onItemClicked } = props;
  const [modalOpen, setModalOpen] = useState(false);

  return (
    <>
      <PlaylistModal
        open={modalOpen}
        close={() => setModalOpen(false)}
        videos={[video]}
      />
      <Popper
        open={open}
        anchorEl={anchorEl}
        placement="bottom-end"
        modifiers={{
          offset: {
            enabled: true,
            offset: "0, 30",
          },
        }}
        style={{
          width: "384px",
          height: "40%",
        }}
      >
        <Paper elevation={3} sx={{ height: "100%" }}>
          <ClickAwayListener onClickAway={closeMenu}>
            <Stack sx={{ height: "100%" }}>
              <ListItem>
                <Typography variant="h5">Playlists</Typography>
              </ListItem>
              <Divider />
              <MenuList
                autoFocusItem={open}
                id="playlist-menu"
                aria-labelledby="composition-button"
                sx={{ overflow: "auto" }}
              >
                {Object.values(store.playlists).map((playlist) => (
                  <MenuItem onClick={() => onItemClicked(playlist, video)}>
                    <div
                      style={{
                        width: 64,
                        height: 64,
                        marginRight: 16,
                      }}
                    >
                      <PlaylistThumbnail
                        videos={store.playlistVideos(playlist.id)}
                      />
                    </div>
                    <Stack direction="column">
                      <ListItemText>{playlist.name}</ListItemText>
                      <ListItemText>
                        {store.playlistVideos(playlist.id).length} medias
                      </ListItemText>
                    </Stack>
                  </MenuItem>
                ))}
              </MenuList>
              <Button
                variant="contained"
                startIcon={<AddIcon />}
                onClick={() => {
                  closeMenu();
                  setModalOpen(true);
                }}
                sx={{
                  height: "40px",
                  transform: "translate(-8px, -40px)",
                  marginBottom: "-32px",
                  marginLeft: "auto",
                  borderRadius: "100px",
                  right: "8px",
                }}
              >
                New playlist
              </Button>
            </Stack>
          </ClickAwayListener>
        </Paper>
      </Popper>
    </>
  );
};

const MediaItem = ({ playlist, video }) => {
  const store = useAppStore();

  const [isHover, setHover] = useState(false);
  const [anchor, setAnchor] = useState(null);
  const isMenuOpen = Boolean(anchor);

  const [anchorPl, setAnchorPl] = useState(null);
  const isPlMenuOpen = Boolean(anchorPl);

  const closeMenu = () => {
    setAnchor(null);
  };

  const closePlMenu = () => {
    setAnchorPl(null);
  };

  const playNext = (video) => {
    closeMenu();
    const playlistIds = queueNext(
      store.playerPlaylist,
      store.player.videoId,
      video.id
    );
    playlistAPI
      .update(store.playerPlaylist.id, { ids: playlistIds })
      .then((_) => {
        if (store.player.isStopped) {
          playerAPI.playMedia(video.id).catch(snackBarHandler(store));
        }
      })
      .catch(snackBarHandler(store));
  };

  const selectPlaylist = () => {
    setAnchorPl(anchor);
    closeMenu();
  };

  const addToPlaylist = (playlist, video) => {
    closePlMenu();
    playlist.ids.push(video.id);
    playlistAPI
      .update(playlist.id, { ids: playlist.ids })
      .catch(snackBarHandler(store));
  };

  const playVideo = (video) => {
    closePlMenu();
    playerAPI.playMedia(video.id).catch(snackBarHandler(store));
  };

  const removePlaylistVideo = (playlist, video) => {
    closePlMenu();
    playlist.ids.splice(playlist.ids.indexOf(video.id), 1);
    playlistAPI.update(playlist.id, { ids: playlist.ids });
  };

  const removeVideo = (video) => {
    closePlMenu();
    videoAPI.delete_(video.id);
  };

  return (
    <ListItem
      sx={{ width: "100%" }}
      onMouseEnter={() => {
        setHover(true);
      }}
      onMouseLeave={() => {
        setHover(false);
      }}
    >
      <MediaQuery minWidth={SIZES.large.min}>
        {(matches) =>
          matches ? (
            <Grid container>
              <Grid item xs={5}>
                <Stack direction="row" alignItems="center">
                  <IconButton
                    sx={{ marginRight: "8px" }}
                    onClick={() => playVideo(video)}
                  >
                    <Avatar alt={video.title} src={video.thumbnail} />
                  </IconButton>
                  <Link
                    href="#"
                    color="inherit"
                    underline="none"
                    onClick={() => playVideo(video)}
                  >
                    <ListItemText>{video.title}</ListItemText>
                  </Link>
                </Stack>
              </Grid>
              <Grid item xs alignSelf="center">
                {video.artist ? (
                  <Link
                    href={`/artists/${video.artist}`}
                    color="inherit"
                    underline="none"
                  >
                    <ListItemText sx={{ color: "#505050" }}>
                      {video.artist}
                    </ListItemText>
                  </Link>
                ) : (
                  <Divider sx={{ width: "24px" }} />
                )}
              </Grid>
              <Grid item xs alignSelf="center">
                {video.album ? (
                  <Link
                    href={`/albums/${video.album}`}
                    color="inherit"
                    underline="none"
                  >
                    <ListItemText sx={{ color: "#505050" }}>
                      {video.album}
                    </ListItemText>
                  </Link>
                ) : (
                  <Divider sx={{ width: "24px" }} />
                )}
              </Grid>
              <Grid item alignSelf="center" xs={1} sx={{ textAlign: "right" }}>
                {isHover || isMenuOpen || isPlMenuOpen ? (
                  <div>
                    <IconButton
                      aria-controls="media-menu"
                      aria-haspopup="true"
                      aria-expanded={isMenuOpen ? "true" : undefined}
                      onClick={(e) => setAnchor(e.currentTarget)}
                    >
                      <MoreVertIcon />
                    </IconButton>
                    <Menu
                      id="media-menu"
                      anchorEl={anchor}
                      open={isMenuOpen}
                      onClose={closeMenu}
                      MenuListProps={{
                        "aria-labelledby": "basic-button",
                      }}
                      transformOrigin={{ horizontal: "right", vertical: "top" }}
                      anchorOrigin={{ horizontal: "right", vertical: "bottom" }}
                    >
                      <MenuItem onClick={() => playNext(video)}>
                        <ListItemIcon>
                          <PlaylistPlayIcon />
                        </ListItemIcon>
                        <ListItemText>Play next</ListItemText>
                      </MenuItem>
                      <MenuItem onClick={selectPlaylist}>
                        <ListItemIcon>
                          <PlaylistAddIcon />
                        </ListItemIcon>
                        <ListItemText>Add to playlist</ListItemText>
                      </MenuItem>
                      {playlist ? (
                        <MenuItem
                          onClick={() => removePlaylistVideo(playlist, video)}
                        >
                          <ListItemIcon>
                            <DeleteOutlineIcon />
                          </ListItemIcon>
                          <ListItemText>Remove from playlist</ListItemText>
                        </MenuItem>
                      ) : (
                        <MenuItem onClick={() => removeVideo(video)}>
                          <ListItemIcon>
                            <DeleteOutlineIcon />
                          </ListItemIcon>
                          <ListItemText>Delete video</ListItemText>
                        </MenuItem>
                      )}
                    </Menu>
                    <PlaylistMenu
                      open={isPlMenuOpen}
                      anchorEl={anchorPl}
                      video={video}
                      closeMenu={closePlMenu}
                      onItemClicked={addToPlaylist}
                    />
                  </div>
                ) : (
                  <ListItemText
                    primary={durationToHMS(video.duration)}
                    sx={{ color: "#505050" }}
                  />
                )}
              </Grid>
            </Grid>
          ) : (
            <Grid container alignItems="center">
              <Grid item xs>
                <Stack direction="row" alignItems="center">
                  <ListItemAvatar>
                    <Avatar alt={video.title} src={video.thumbnail} />
                  </ListItemAvatar>
                  <Stack>
                    <Typography>{video.title}</Typography>{" "}
                    <Typography sx={{ color: "#505050" }}>
                      {renderArtistAlbum(video)}
                    </Typography>
                  </Stack>
                </Stack>
              </Grid>
              <Grid item alignSelf="center">
                <ListItemText
                  primary={durationToHMS(video.duration)}
                  sx={{ textAlign: "right", color: "#505050" }}
                />
              </Grid>
            </Grid>
          )
        }
      </MediaQuery>
    </ListItem>
  );
};

export default MediaItem;
