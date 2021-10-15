import { useState } from "react";

import {
  Avatar,
  Box,
  IconButton,
  Grid,
  Link,
  ListItem,
  ListItemAvatar,
  ListItemIcon,
  ListItemText,
  Menu,
  MenuItem,
  Stack,
  Typography,
} from "@mui/material";
import MoreVertIcon from "@mui/icons-material/MoreVert";
import PlaylistPlayIcon from "@mui/icons-material/PlaylistPlay";
import PlaylistAddIcon from "@mui/icons-material/PlaylistAdd";
import DeleteOutlineIcon from "@mui/icons-material/DeleteOutline";

import MediaQuery from "react-responsive";
import { SIZES } from "constants.js";

import { durationToHMS } from "services/duration";
import playlistAPI from "services/api/playlist";
import playerAPI from "services/api/player";
import videoAPI from "services/api/video";

import { useAppStore } from "components/app_context";

import PlaylistThumbnail from "components/playlist_thumbnail";

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

  const selectPlaylist = () => {
    setAnchorPl(anchor);
    closeMenu();
  };

  const addToPlaylist = (playlist, video) => {
    closePlMenu();
    playlist.ids.push(video.id);
    playlistAPI.update(playlist.id, { ids: playlist.ids });
  };

  const playVideo = (video) => {
    closePlMenu();
    playerAPI.playMedia(video.id).catch((error) => console.log(error));
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
                <ListItemText sx={{ color: "#505050" }}>
                  {"Artist"}
                </ListItemText>
              </Grid>
              <Grid item xs alignSelf="center">
                <ListItemText sx={{ color: "#505050" }}>{"Album"}</ListItemText>
              </Grid>
              <Grid item alignSelf="center" xs={1} sx={{ textAlign: "right" }}>
                {isHover ? (
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
                    >
                      <MenuItem onClick={closeMenu}>
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
                    <Menu
                      id="playlist-menu"
                      anchorEl={anchorPl}
                      open={isPlMenuOpen}
                      onClose={closePlMenu}
                      MenuListProps={{
                        "aria-labelledby": "basic-button",
                      }}
                      sx={{ display: "flex" }}
                    >
                      <Box>
                        <ListItem>
                          <Typography variant="h6" sx={{ fontWeight: 600 }}>
                            All playlists
                          </Typography>
                        </ListItem>
                        {Object.values(store.playlists).map((playlist) => (
                          <MenuItem
                            onClick={() => addToPlaylist(playlist, video)}
                          >
                            <div
                              style={{ width: 64, height: 64, marginRight: 16 }}
                            >
                              <PlaylistThumbnail
                                videos={store.playlistVideos(playlist.id)}
                              />
                            </div>
                            <Stack direction="column">
                              <ListItemText>{playlist.name}</ListItemText>
                              <ListItemText>
                                {store.playlistVideos(playlist.id).length}
                                medias
                              </ListItemText>
                            </Stack>
                          </MenuItem>
                        ))}
                      </Box>
                    </Menu>
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
                      {"Artist • Album"}
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
