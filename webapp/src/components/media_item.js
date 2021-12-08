import { memo, useState, useCallback } from "react";

import {
  Avatar,
  Box,
  Button,
  Divider,
  IconButton,
  ListItem,
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
import QueueMusicIcon from "@mui/icons-material/QueueMusic";
import PlayArrowIcon from "@mui/icons-material/PlayArrow";
import VolumeUpIcon from "@mui/icons-material/VolumeUp";
import AudiotrackIcon from "@mui/icons-material/Audiotrack";

import Popper from "@mui/material/Popper";
import ClickAwayListener from "@mui/material/ClickAwayListener";
import MenuList from "@mui/material/MenuList";

import { styled } from "@mui/material/styles";

import { Link } from "react-router-dom";

import { observer } from "mobx-react-lite";

import { durationToHMS } from "services/duration";
import { queueNext, queueLast } from "services/playlist";
import playlistAPI from "services/api/playlist";
import playerAPI from "services/api/player";
import videoAPI from "services/api/video";
import snackBarHandler from "services/api/error";

import { useAppStore } from "components/app_context";

import { PlaylistThumbnail } from "components/playlist_thumbnail";
import PlaylistModal from "components/playlist_modal";

const pluralize = require("pluralize");

const StyledLink = styled((props) => <Link {...props} />)({
  color: "inherit",
  textDecoration: "none",
});

const ClickableBox = styled(Box)({
  cursor: "pointer",
});

const playVideo = (video, store) => {
  const playerPlaylist = store.playerPlaylist;

  if (playerPlaylist.ids.includes(video.id)) {
    if (video.id === store.player.videoId) {
      playerAPI.pauseMedia(video.id).catch(snackBarHandler(store));
    } else {
      playerAPI.playMedia(video.id).catch(snackBarHandler(store));
    }
  } else {
    const ids = queueNext(playerPlaylist, store.player.videoId, [video.id]);
    playlistAPI
      .update(playerPlaylist.id, { ids: ids })
      .then(() => {
        playerAPI.playMedia(video.id).catch(snackBarHandler(store));
      })
      .catch(snackBarHandler(store));
  }
};

const MediaSecondaryData = ({ artist, album, duration }) => {
  const artistBloc = artist ? (
    <StyledLink
      to={`/library/artists/${artist.id}`}
      style={{ whiteSpace: "nowrap" }}
    >
      {artist.name}
    </StyledLink>
  ) : (
    <div style={{ whiteSpace: "nowrap" }}>Artist</div>
  );

  const albumBloc = album ? (
    <StyledLink
      to={`/library/albums/${album.id}`}
      style={{ whiteSpace: "nowrap" }}
    >
      • {album.name}
    </StyledLink>
  ) : (
    <div style={{ whiteSpace: "nowrap" }}>• Album</div>
  );

  const HMSDuration = durationToHMS(duration);
  return (
    <Stack
      direction="row"
      alignItems="center"
      sx={{ minWidth: "0px", color: "#505050" }}
    >
      <Box
        sx={{
          marginRight: "4px",
          minWidth: "0px",
          overflow: "hidden",
          textOverflow: "ellipsis",
        }}
      >
        {artistBloc}
      </Box>
      <Box
        sx={{
          marginRight: "4px",
          minWidth: "0px",
          overflow: "hidden",
          textOverflow: "ellipsis",
        }}
      >
        {albumBloc}
      </Box>
      <Stack direction="row" sx={{ whiteSpace: "nowrap" }}>
        • {HMSDuration}
      </Stack>
    </Stack>
  );
};

const PlaylistMenu = (props) => {
  const store = useAppStore();

  const { anchorEl, video, closeMenu } = props;
  const [modalOpen, setModalOpen] = useState(false);
  const open = Boolean(anchorEl);

  const addToPlaylist = (playlist, video) => {
    closeMenu();
    playlist.ids.push(video.id);
    playlistAPI
      .update(playlist.id, { ids: playlist.ids })
      .catch(snackBarHandler(store));
  };

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
        style={{
          width: "min(400px, 75%)",
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
                  <MenuItem
                    key={playlist.id}
                    onClick={() => addToPlaylist(playlist, video)}
                  >
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
                        {pluralize(
                          "media",
                          store.playlistVideos(playlist.id).length,
                          true
                        )}
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

const MediaItemMenu = (props) => {
  const store = useAppStore();
  const { anchorEl, setAnchorPl, playlist, video, closeMenu } = props;
  const isOpen = Boolean(anchorEl);

  const playNext = (video) => {
    closeMenu();
    const playlistIds = queueNext(store.playerPlaylist, store.player.videoId, [
      video.id,
    ]);
    playlistAPI
      .update(store.playerPlaylist.id, { ids: playlistIds })
      .then((_) => {
        if (store.player.isStopped) {
          playerAPI.playMedia(video.id).catch(snackBarHandler(store));
        }
      })
      .catch(snackBarHandler(store));
  };

  const queue = (video) => {
    closeMenu();
    const playlistIds = queueLast(store.playerPlaylist, store.player.videoId, [
      video.id,
    ]);
    playlistAPI
      .update(store.playerPlaylist.id, { ids: playlistIds })
      .then((_) => {
        store.enqueueSnackbar({
          message: video.title + " queued",
          options: {
            variant: "success",
          },
        });
      })
      .catch(snackBarHandler(store));
  };

  const selectPlaylist = () => {
    setAnchorPl(anchorEl);
    closeMenu();
  };

  const removePlaylistVideo = (playlist, video) => {
    closeMenu();
    playlist.ids.splice(playlist.ids.indexOf(video.id), 1);
    playlistAPI.update(playlist.id, { ids: playlist.ids });
  };

  const removeVideo = (video) => {
    closeMenu();
    videoAPI.delete_(video.id);
  };
  return (
    <Menu
      id="media-menu"
      anchorEl={anchorEl}
      open={isOpen}
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
      <MenuItem onClick={() => queue(video)}>
        <ListItemIcon>
          <QueueMusicIcon />
        </ListItemIcon>
        <ListItemText>Add to queue</ListItemText>
      </MenuItem>
      <MenuItem onClick={selectPlaylist}>
        <ListItemIcon>
          <PlaylistAddIcon />
        </ListItemIcon>
        <ListItemText>Add to playlist</ListItemText>
      </MenuItem>
      {playlist ? (
        <MenuItem onClick={() => removePlaylistVideo(playlist, video)}>
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
  );
};

const PlayingMediaAvatar = observer(({ video, isPlaying, onClick }) => {
  return (
    <IconButton sx={{ marginRight: "8px" }} onClick={onClick}>
      {video.thumbnail ? (
        <Avatar
          alt={video.title}
          src={video.thumbnail}
          sx={{
            background:
              "linear-gradient(to bottom right, #C6FFDD 0%, #FBD786 50%, #F7797D 100%)",
          }}
        />
      ) : (
        <Avatar
          alt={video.title}
          sx={{
            background:
              "linear-gradient(to bottom right, #C6FFDD 0%, #FBD786 50%, #F7797D 100%)",
          }}
        >
          <AudiotrackIcon />
        </Avatar>
      )}
      <Box
        justifyContent="center"
        alignItems="center"
        sx={{
          display: "flex",
          height: "40px",
          width: "40px",
          position: "absolute",
          backgroundColor: "rgba(0,0,0,0.3)",
          borderRadius: "100%",
        }}
      >
        {isPlaying ? (
          <VolumeUpIcon sx={{ color: "#F5F5F5" }} />
        ) : (
          <PlayArrowIcon sx={{ color: "#F5F5F5" }} />
        )}
      </Box>
    </IconButton>
  );
});

const MediaAvatar = memo(({ video, isHover, onClick }) => {
  return (
    <IconButton
      sx={{
        marginRight: "8px",
      }}
      onClick={onClick}
    >
      {video.thumbnail ? (
        <Avatar
          alt={video.title}
          src={video.thumbnail}
          sx={{
            background:
              "linear-gradient(to bottom right, #C6FFDD 0%, #FBD786 50%, #F7797D 100%)",
          }}
        />
      ) : (
        <Avatar
          alt={video.title}
          sx={{
            background:
              "linear-gradient(to bottom right, #C6FFDD 0%, #FBD786 50%, #F7797D 100%)",
          }}
        >
          <AudiotrackIcon sx={{ color: "rgba(0,0,0,0.5)" }} />
        </Avatar>
      )}
      {isHover && (
        <Box
          justifyContent="center"
          alignItems="center"
          sx={{
            display: "flex",
            height: "40px",
            width: "40px",
            position: "absolute",
            backgroundColor: "rgba(0,0,0,0.33)",
            borderRadius: "100%",
          }}
        >
          <PlayArrowIcon sx={{ color: "#F5F5F5" }} />
        </Box>
      )}
    </IconButton>
  );
});

const MediaItem = observer((props) => {
  const store = useAppStore();

  const {
    children,
    isSmallDevice,
    video,
    isActive,
    playlist = null,
    showOptions = true,
  } = props;

  const [isHover, setHover] = useState(false);
  const [anchor, setAnchor] = useState(null);
  const isMenuOpen = Boolean(anchor);

  const [anchorPl, setAnchorPl] = useState(null);
  const isPlMenuOpen = Boolean(anchorPl);

  const artist = store.artists[video.artist_id];
  const album = store.albums[video.album_id];

  const closeMenu = useCallback(() => {
    setAnchor(null);
  }, []);

  const closePlMenu = useCallback(() => {
    setAnchorPl(null);
  }, []);

  const playVideoCallback = useCallback(
    () => playVideo(video, store),
    [video, store]
  );

  const pauseMedia = useCallback(
    () => playerAPI.pauseMedia().catch(snackBarHandler(store)),
    [store]
  );

  const openMenu = useCallback((e) => setAnchor(e.currentTarget), [setAnchor]);

  if (!isSmallDevice) {
    return (
      <ListItem
        sx={{ width: "100%", paddingLeft: "0px", paddingRight: "8px" }}
        onMouseEnter={() => {
          setHover(true);
        }}
        onMouseLeave={() => {
          setHover(false);
        }}
      >
        <Box
          direction="row"
          alignItems="center"
          sx={{ display: "flex", flex: "1 1 auto" }}
        >
          <Box sx={{ flex: "none" }}>
            {isActive ? (
              <PlayingMediaAvatar
                video={video}
                isPlaying={store.player.isPlaying}
                onClick={pauseMedia}
              />
            ) : (
              <MediaAvatar
                video={video}
                isHover={isHover}
                onClick={playVideoCallback}
              />
            )}
          </Box>
          <Box sx={{ display: "flex", flex: "1 1 0%" }}>
            <Box
              sx={{
                display: "flex",
                flex: "6 1 0",
                justifyContent: "space-between",
              }}
            >
              <ClickableBox onClick={() => playVideo(video, store)}>
                <ListItemText>{video.title}</ListItemText>
              </ClickableBox>
            </Box>
            <Box sx={{ display: "flex", flex: "9 1 0", alignItems: "center" }}>
              <Box sx={{ flex: "1 1 0%" }}>
                {artist ? (
                  <StyledLink
                    to={`/library/artists/${artist.id}`}
                    color="inherit"
                    underline="none"
                  >
                    <ListItemText sx={{ color: "#505050" }}>
                      {artist.name}
                    </ListItemText>
                  </StyledLink>
                ) : (
                  <Divider sx={{ width: "24px" }} />
                )}
              </Box>
              <Box sx={{ flex: "1 1 0%" }}>
                {album ? (
                  <StyledLink
                    to={`/library/albums/${album.id}`}
                    color="inherit"
                    underline="none"
                  >
                    <ListItemText sx={{ color: "#505050" }}>
                      {album.name}
                    </ListItemText>
                  </StyledLink>
                ) : (
                  <Divider sx={{ width: "24px" }} />
                )}
              </Box>
            </Box>
          </Box>
          <Box sx={{ display: "inline-flex", flex: "0 1 auto" }}>
            {showOptions && (isHover || isMenuOpen || isPlMenuOpen) ? (
              <IconButton
                aria-controls="media-menu"
                aria-haspopup="true"
                aria-expanded={isMenuOpen ? "true" : undefined}
                onClick={openMenu}
              >
                <MoreVertIcon />
              </IconButton>
            ) : (
              <div
                style={{
                  height: "40px",
                  width: "40px",
                  visibility: "hidden",
                }}
              />
            )}
            {children}
          </Box>
          <Box sx={{ display: "flex" }}>
            <ListItemText
              primary={durationToHMS(video.duration)}
              sx={{
                width: "54px",
                color: "#505050",
                marginRight: "8px",
                textAlign: "end",
              }}
            />
          </Box>
        </Box>
        <div>
          {anchor && (
            <MediaItemMenu
              anchorEl={anchor}
              setAnchorPl={setAnchorPl}
              playlist={playlist}
              video={video}
              closeMenu={closeMenu}
            />
          )}
          {anchorPl && (
            <PlaylistMenu
              anchorEl={anchorPl}
              video={video}
              closeMenu={closePlMenu}
            />
          )}
        </div>
      </ListItem>
    );
  }

  return (
    <ListItem sx={{ width: "100%", paddingLeft: "0px", paddingRight: "8px" }}>
      <Stack
        direction="row"
        alignItems="center"
        sx={{ minWidth: "0px", flex: 1 }}
      >
        {isActive ? (
          <PlayingMediaAvatar
            video={video}
            isPlaying={store.player.isPlaying}
            onClick={pauseMedia}
          />
        ) : (
          <MediaAvatar
            video={video}
            isHover={isHover}
            onClick={playVideoCallback}
          />
        )}
        <Box sx={{ flex: 1, minWidth: "0px" }}>
          <ClickableBox onClick={() => playVideo(video, store)}>
            <Typography noWrap>{video.title}</Typography>
          </ClickableBox>
          <MediaSecondaryData
            artist={artist}
            album={album}
            duration={video.duration}
          />
        </Box>
        <div>
          {children}
          {showOptions && (
            <IconButton
              aria-controls="media-menu"
              aria-haspopup="true"
              aria-expanded={isMenuOpen ? "true" : undefined}
              onClick={openMenu}
            >
              <MoreVertIcon />
            </IconButton>
          )}
        </div>
      </Stack>
      <div>
        {anchor && (
          <MediaItemMenu
            anchorEl={anchor}
            setAnchorPl={setAnchorPl}
            playlist={playlist}
            video={video}
            closeMenu={closeMenu}
          />
        )}
        {anchorPl && (
          <PlaylistMenu
            anchorEl={anchorPl}
            video={video}
            closeMenu={closePlMenu}
          />
        )}
      </div>
    </ListItem>
  );
});

export { MediaItem, MediaAvatar, PlayingMediaAvatar };
