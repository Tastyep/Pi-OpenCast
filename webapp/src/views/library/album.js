import { useState } from "react";

import Box from "@mui/material/Box";
import Button from "@mui/material/Button";
import Divider from "@mui/material/Divider";
import IconButton from "@mui/material/IconButton";
import List from "@mui/material/List";
import ListItemText from "@mui/material/ListItemText";
import ListItemIcon from "@mui/material/ListItemIcon";
import Menu from "@mui/material/Menu";
import MenuItem from "@mui/material/MenuItem";
import Typography from "@mui/material/Typography";
import Stack from "@mui/material/Stack";

import ShuffleIcon from "@mui/icons-material/Shuffle";
import PlaylistPlayIcon from "@mui/icons-material/PlaylistPlay";
import QueueMusicIcon from "@mui/icons-material/QueueMusic";
import MoreVertIcon from "@mui/icons-material/MoreVert";
import AlbumIcon from "@mui/icons-material/Album";

import { useParams } from "react-router-dom";

import { observer } from "mobx-react-lite";

import { useMediaQuery } from "react-responsive";
import { SIZES } from "constants.js";

import { queueNext, queueLast, shuffleIds } from "services/playlist";
import playlistAPI from "services/api/playlist";
import playerAPI from "services/api/player";
import snackBarHandler from "services/api/error";
import { humanReadableDuration } from "services/duration";

import { useAppStore } from "components/app_context";
import { MediaItem } from "components/media_item";

const pluralize = require("pluralize");

const AlbumMenu = (props) => {
  const store = useAppStore();
  const { open, anchorEl, album, closeMenu } = props;

  const playNext = () => {
    closeMenu();

    const playlistIds = queueNext(
      store.playerPlaylist,
      store.player.videoId,
      album.ids
    );
    playlistAPI
      .update(store.playerPlaylist.id, { ids: playlistIds })
      .then((_) => {
        if (store.player.isStopped) {
          playerAPI.playMedia(album.ids[0]).catch(snackBarHandler(store));
        }
      })
      .catch(snackBarHandler(store));
  };

  const queue = () => {
    closeMenu();

    const playlistIds = queueLast(
      store.playerPlaylist,
      store.player.videoId,
      album.ids
    );
    playlistAPI
      .update(store.playerPlaylist.id, { ids: playlistIds })
      .then((_) => {
        store.enqueueSnackbar({
          message: album.name + " queued",
          options: {
            variant: "success",
          },
        });
      })
      .catch(snackBarHandler(store));
  };

  return (
    <Menu
      id="album-menu"
      anchorEl={anchorEl}
      open={open}
      onClose={closeMenu}
      MenuListProps={{
        "aria-labelledby": "basic-button",
      }}
      transformOrigin={{ horizontal: "right", vertical: "top" }}
      anchorOrigin={{ horizontal: "right", vertical: "bottom" }}
    >
      <MenuItem onClick={playNext}>
        <ListItemIcon>
          <PlaylistPlayIcon />
        </ListItemIcon>
        <ListItemText>Play next</ListItemText>
      </MenuItem>
      <MenuItem onClick={queue}>
        <ListItemIcon>
          <QueueMusicIcon />
        </ListItemIcon>
        <ListItemText>Add to queue</ListItemText>
      </MenuItem>
    </Menu>
  );
};

const AlbumPage = observer(() => {
  const store = useAppStore();
  const { id } = useParams();

  const [anchor, setAnchor] = useState(null);
  const isMenuOpen = Boolean(anchor);

  const isSmallDevice = useMediaQuery({
    maxWidth: SIZES.small.max,
  });

  const album = store.albums[id];
  if (!album) {
    return null;
  }

  const albumVideos = store.filterVideos(album.ids);

  const shufflePlayNext = () => {
    const shuffledIds = shuffleIds(album.ids);
    const playlistIds = queueNext(
      store.playerPlaylist,
      store.player.videoId,
      shuffledIds
    );
    playlistAPI
      .update(store.playerPlaylist.id, { ids: playlistIds })
      .then((_) => {
        if (store.player.isStopped) {
          playerAPI.playMedia(shuffledIds[0]).catch(snackBarHandler(store));
        }
      })
      .catch(snackBarHandler(store));
  };

  const totalDuration = () => {
    let total = 0;

    for (const video of albumVideos) {
      total += video.duration;
    }

    return humanReadableDuration(total);
  };

  if (!album) {
    return null;
  }

  return (
    <Stack sx={{ height: "100%", width: "100%" }}>
      <Box
        sx={{
          marginTop: "32px",
          marginBottom: "24px",
          marginLeft: "16px",
        }}
      >
        <Stack direction="row" alignItems="center">
          <Box
            sx={{
              display: "flex",
              minWidth: "64px",
              maxWidth: "128px",
              aspectRatio: "1/1",
              justifyContent: "center",
              alignItems: "center",
              marginRight: "32px",
              borderRadius: "8px",
              overflow: "hidden",
              background:
                "linear-gradient(to bottom right, #C6FFDD 0%, #FBD786 50%, #F7797D 100%)",
              caretColor: "transparent",
            }}
          >
            {album.thumbnail ? (
              <img
                src={album.thumbnail}
                alt={album.name}
                style={{
                  height: "100%",
                  width: "100%",
                  objectFit: "cover",
                }}
              />
            ) : (
              <AlbumIcon
                sx={{ height: "64%", width: "64%", color: "rgba(0,0,0,0.6)" }}
              />
            )}
          </Box>
          <div>
            <Typography
              variant="h5"
              sx={{ maxHeight: "60px", overflow: "hidden" }}
            >
              {album.name}
            </Typography>
            <Typography>
              {pluralize("media", albumVideos.length, true)}
            </Typography>
            <Typography>{totalDuration()}</Typography>
          </div>
        </Stack>
        <Stack direction="row" sx={{ marginTop: "16px" }}>
          <Box>
            <Button
              disableElevation
              variant="contained"
              startIcon={<ShuffleIcon />}
              sx={{ alignItems: "flex-start", marginRight: "8px" }}
              onClick={() => shufflePlayNext()}
            >
              Shuffle
            </Button>
          </Box>
          <IconButton
            aria-controls="album-menu"
            aria-haspopup="true"
            aria-expanded={isMenuOpen ? "true" : undefined}
            onClick={(e) => setAnchor(e.currentTarget)}
          >
            <MoreVertIcon />
          </IconButton>
          <AlbumMenu
            open={isMenuOpen}
            anchorEl={anchor}
            album={album}
            closeMenu={() => setAnchor(null)}
          />
        </Stack>
      </Box>
      <Divider />
      <Box
        sx={{
          height: "100%",
          width: "100%",
          overflow: "auto",
        }}
      >
        <List sx={{ height: "100%", width: "100%", padding: "0px" }}>
          {albumVideos.map((video) => (
            <MediaItem
              key={video.id}
              isSmallDevice={isSmallDevice}
              video={video}
              isActive={video.id === store.player.videoId}
            />
          ))}
        </List>
      </Box>
    </Stack>
  );
});

export default AlbumPage;
