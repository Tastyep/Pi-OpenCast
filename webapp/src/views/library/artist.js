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
import ArtistThumbnail from "components/artist_thumbnail";
import { MediaItem } from "components/media_item";

const pluralize = require("pluralize");

const ArtistMenu = (props) => {
  const store = useAppStore();
  const { open, anchorEl, artist, closeMenu } = props;

  const playNext = () => {
    closeMenu();

    const ids = artist.videos.map((video) => video.id);
    const playlistIds = queueNext(
      store.playerPlaylist,
      store.player.videoId,
      ids
    );
    playlistAPI
      .update(store.playerPlaylist.id, { ids: playlistIds })
      .then((_) => {
        if (store.player.isStopped) {
          playerAPI.playMedia(playlistIds[0]).catch(snackBarHandler(store));
        }
      })
      .catch(snackBarHandler(store));
  };

  const queue = (playlist) => {
    closeMenu();

    const ids = artist.videos.map((video) => video.id);
    const playlistIds = queueLast(
      store.playerPlaylist,
      store.player.videoId,
      ids
    );
    playlistAPI
      .update(store.playerPlaylist.id, { ids: playlistIds })
      .then((_) => {
        store.enqueueSnackbar({
          message: artist.name + " queued",
          options: {
            variant: "success",
          },
        });
      })
      .catch(snackBarHandler(store));
  };

  return (
    <Menu
      id="artist-menu"
      anchorEl={anchorEl}
      open={open}
      onClose={closeMenu}
      MenuListProps={{
        "aria-labelledby": "basic-button",
      }}
      transformOrigin={{ horizontal: "right", vertical: "top" }}
      anchorOrigin={{ horizontal: "right", vertical: "bottom" }}
    >
      <MenuItem onClick={() => playNext()}>
        <ListItemIcon>
          <PlaylistPlayIcon />
        </ListItemIcon>
        <ListItemText>Play next</ListItemText>
      </MenuItem>
      <MenuItem onClick={() => queue()}>
        <ListItemIcon>
          <QueueMusicIcon />
        </ListItemIcon>
        <ListItemText>Add to queue</ListItemText>
      </MenuItem>
    </Menu>
  );
};

const ArtistPage = observer(() => {
  const store = useAppStore();
  const { name } = useParams();

  const [anchor, setAnchor] = useState(null);
  const isMenuOpen = Boolean(anchor);

  const artist = store.artists()[name];

  const isSmallDevice = useMediaQuery({
    maxWidth: SIZES.small.max,
  });

  const shufflePlayNext = () => {
    const ids = artist.videos.map((video) => {
      return video.id;
    });

    const playlistIds = queueNext(
      store.playerPlaylist,
      store.player.videoId,
      shuffleIds(ids)
    );
    playlistAPI
      .update(store.playerPlaylist.id, { ids: playlistIds })
      .then((_) => {
        if (store.player.isStopped) {
          playerAPI.playMedia(playlistIds[0]).catch(snackBarHandler(store));
        }
      })
      .catch(snackBarHandler(store));
  };

  const totalDuration = () => {
    let total = 0;

    for (const video of artist.videos) {
      total += video.duration;
    }

    return humanReadableDuration(total);
  };

  if (!artist) {
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
              width: "128px",
              height: "128px",
              marginRight: "32px",
              borderRadius: "8px",
              overflow: "hidden",
            }}
          >
            <ArtistThumbnail albums={artist.albums} />
          </Box>
          <Box>
            <Typography variant="h4">{name}</Typography>
            <Typography>
              {pluralize("media", artist.videos.length, true)}
            </Typography>
            <Typography>{totalDuration()}</Typography>
          </Box>
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
            aria-controls="artist-menu"
            aria-haspopup="true"
            aria-expanded={isMenuOpen ? "true" : undefined}
            onClick={(e) => setAnchor(e.currentTarget)}
          >
            <MoreVertIcon />
          </IconButton>
          <ArtistMenu
            open={isMenuOpen}
            anchorEl={anchor}
            artist={artist}
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
          {artist.videos.map((video) => (
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

export default ArtistPage;
