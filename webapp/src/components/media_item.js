import { useState } from "react";

import {
  Avatar,
  Box,
  Button,
  Divider,
  IconButton,
  Grid,
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

import Popper from "@mui/material/Popper";
import ClickAwayListener from "@mui/material/ClickAwayListener";
import MenuList from "@mui/material/MenuList";

import { styled } from "@mui/material/styles";

import { Link } from "react-router-dom";

import { useMediaQuery } from "react-responsive";
import { SIZES } from "constants.js";

import { observer } from "mobx-react-lite";

import { durationToHMS } from "services/duration";
import { queueNext, queueLast } from "services/playlist";
import playlistAPI from "services/api/playlist";
import playerAPI from "services/api/player";
import videoAPI from "services/api/video";
import snackBarHandler from "services/api/error";

import { useAppStore } from "components/app_context";

import PlaylistThumbnail from "components/playlist_thumbnail";
import PlaylistModal from "components/playlist_modal";

const pluralize = require("pluralize");

const StyledLink = styled(Link)({
  color: "inherit",
  textDecoration: "none",
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

const renderMediaSecondaryData = (video) => {
  const artist = video.artist ? (
    <StyledLink to={`/library/artists/${video.artist}`}>
      {video.artist}
    </StyledLink>
  ) : (
    "Artist"
  );

  const album = video.album ? (
    <StyledLink to={`/library/albums/${video.album}`}>{video.album}</StyledLink>
  ) : (
    "Album"
  );

  const duration = durationToHMS(video.duration);

  return (
    <Grid
      container
      direction="row"
      sx={{ flexWrap: "nowrap", color: "#505050", minWidth: "0px" }}
    >
      <Grid item zeroMinWidth>
        <Typography noWrap>{artist}</Typography>
      </Grid>
      <Grid item zeroMinWidth>
        <Stack direction="row">
          <Typography sx={{ padding: "0px 4px" }}>•</Typography>
          <Typography noWrap>{album}</Typography>
        </Stack>
      </Grid>
      <Grid item>
        <Stack direction="row">
          <Typography sx={{ padding: "0px 4px" }}>•</Typography>
          <Typography noWrap>{duration}</Typography>
        </Stack>
      </Grid>
    </Grid>
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
                    onClick={() => onItemClicked(playlist, video)}
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

const PlayingMediaAvatar = observer(({ video, isPlaying, onClick }) => {
  const store = useAppStore();

  return (
    <IconButton sx={{ marginRight: "8px" }} onClick={onClick}>
      <Avatar alt={video.title} src={video.thumbnail} />
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
        {isPlaying ? (
          <VolumeUpIcon sx={{ color: "#F5F5F5" }} />
        ) : (
          <PlayArrowIcon sx={{ color: "#F5F5F5" }} />
        )}
      </Box>
    </IconButton>
  );
});

const MediaAvatar = ({ video, isHover, onClick }) => {
  return (
    <IconButton sx={{ marginRight: "8px" }} onClick={onClick}>
      <Avatar alt={video.title} src={video.thumbnail} />
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
};

const MediaItem = observer(({ video, isActive, playlist }) => {
  const store = useAppStore();

  const [isHover, setHover] = useState(false);
  const [anchor, setAnchor] = useState(null);
  const isMenuOpen = Boolean(anchor);

  const [anchorPl, setAnchorPl] = useState(null);
  const isPlMenuOpen = Boolean(anchorPl);

  const isLargeDevice = useMediaQuery({
    minWidth: SIZES.large.min,
  });

  const closeMenu = () => {
    setAnchor(null);
  };

  const closePlMenu = () => {
    setAnchorPl(null);
  };

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
      sx={{ width: "100%", paddingLeft: "0px", paddingRight: "8px" }}
      onMouseEnter={() => {
        setHover(true);
      }}
      onMouseLeave={() => {
        setHover(false);
      }}
    >
      {isLargeDevice ? (
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
                onClick={() => {
                  playerAPI.pauseMedia().catch(snackBarHandler(store));
                }}
              />
            ) : (
              <MediaAvatar
                video={video}
                isHover={isHover}
                onClick={() => playVideo(video, store)}
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
              <StyledLink to="#" onClick={() => playVideo(video, store)}>
                <ListItemText>{video.title}</ListItemText>
              </StyledLink>
            </Box>
            <Box sx={{ display: "flex", flex: "9 1 0", alignItems: "center" }}>
              <Box sx={{ flex: "1 1 0%" }}>
                {video.artist ? (
                  <StyledLink
                    to={`/library/artists/${video.artist}`}
                    color="inherit"
                    underline="none"
                  >
                    <ListItemText sx={{ color: "#505050" }}>
                      {video.artist}
                    </ListItemText>
                  </StyledLink>
                ) : (
                  <Divider sx={{ width: "24px" }} />
                )}
              </Box>
              <Box sx={{ flex: "1 1 0%" }}>
                {video.album ? (
                  <StyledLink
                    to={`/library/albums/${video.album}`}
                    color="inherit"
                    underline="none"
                  >
                    <ListItemText sx={{ color: "#505050" }}>
                      {video.album}
                    </ListItemText>
                  </StyledLink>
                ) : (
                  <Divider sx={{ width: "24px" }} />
                )}
              </Box>
            </Box>
          </Box>
          <Box sx={{ width: "40px" }}>
            {isHover || isMenuOpen || isPlMenuOpen ? (
              <IconButton
                aria-controls="media-menu"
                aria-haspopup="true"
                aria-expanded={isMenuOpen ? "true" : undefined}
                onClick={(e) => setAnchor(e.currentTarget)}
              >
                <MoreVertIcon />
              </IconButton>
            ) : null}
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
      ) : (
        <Grid container alignItems="center" flexWrap="nowrap">
          <Grid
            item
            container
            xs
            zeroMinWidth
            direction="row"
            flexWrap="nowrap"
          >
            {isActive ? (
              <PlayingMediaAvatar
                video={video}
                isPlaying={store.player.isPlaying}
                onClick={() => {
                  playerAPI.pauseMedia().catch(snackBarHandler(store));
                }}
              />
            ) : (
              <MediaAvatar
                video={video}
                isHover={isHover}
                onClick={() => playVideo(video, store)}
              />
            )}
            <Stack sx={{ minWidth: "0px" }}>
              <StyledLink
                to="#"
                color="inherit"
                underline="none"
                onClick={() => playVideo(video, store)}
              >
                <Typography noWrap>{video.title}</Typography>
              </StyledLink>
              {renderMediaSecondaryData(video)}
            </Stack>
          </Grid>
          <Grid item alignSelf="center">
            <IconButton
              aria-controls="media-menu"
              aria-haspopup="true"
              aria-expanded={isMenuOpen ? "true" : undefined}
              onClick={(e) => setAnchor(e.currentTarget)}
            >
              <MoreVertIcon />
            </IconButton>
          </Grid>
        </Grid>
      )}
      <div>
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
        <PlaylistMenu
          open={isPlMenuOpen}
          anchorEl={anchorPl}
          video={video}
          closeMenu={closePlMenu}
          onItemClicked={addToPlaylist}
        />
      </div>
    </ListItem>
  );
});

export { MediaItem, MediaAvatar, PlayingMediaAvatar };
