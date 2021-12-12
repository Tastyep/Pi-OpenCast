import { useState } from "react";

import Box from "@mui/material/Box";
import Button from "@mui/material/Button";
import Divider from "@mui/material/Divider";
import IconButton from "@mui/material/IconButton";
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

import { useParams, useNavigate } from "react-router-dom";

import { observer } from "mobx-react-lite";

import { queueNext, queueLast, shuffleIds } from "services/playlist";
import playlistAPI from "services/api/playlist";
import playerAPI from "services/api/player";
import snackBarHandler from "services/api/error";
import { humanReadableDuration } from "services/duration";

import { useAppStore } from "components/app_context";
import { ArtistThumbnail } from "components/artist_thumbnail";
import { VirtualizedMediaList } from "components/media_list";

const pluralize = require("pluralize");

const ArtistMenu = (props) => {
  const store = useAppStore();
  const { open, anchorEl, artist, closeMenu } = props;

  const playNext = () => {
    closeMenu();

    const playlistIds = queueNext(
      store.playerPlaylist,
      store.player.videoId,
      artist.ids
    );
    playlistAPI
      .update(store.playerPlaylist.id, { ids: playlistIds })
      .then((_) => {
        if (store.player.isStopped) {
          playerAPI.playMedia(artist.ids[0]).catch(snackBarHandler(store));
        }
      })
      .catch(snackBarHandler(store));
  };

  const queue = () => {
    closeMenu();

    const playlistIds = queueLast(
      store.playerPlaylist,
      store.player.videoId,
      artist.ids
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

const ArtistPage = observer(() => {
  const store = useAppStore();
  const { id } = useParams();

  const [anchor, setAnchor] = useState(null);
  const isMenuOpen = Boolean(anchor);
  let navigate = useNavigate();

  const artist = store.artists[id];
  if (!artist) {
    return null;
  }

  if (artist.ids.length === 0) {
    navigate("/library");
  }

  const artistVideos = store.filterVideos(artist.ids);

  const shufflePlayNext = () => {
    const shuffledIds = shuffleIds(artist.ids);
    const playlistIds = queueNext(
      store.playerPlaylist,
      store.player.videoId,
      shuffledIds
    );
    playlistAPI
      .update(store.playerPlaylist.id, { ids: playlistIds })
      .then((_) => {
        if (store.player.videoId !== shuffledIds[0]) {
          playerAPI.playMedia(shuffledIds[0]).catch(snackBarHandler(store));
        }
      })
      .catch(snackBarHandler(store));
  };

  const totalDuration = () => {
    let total = 0;

    for (const video of artistVideos) {
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
          <Stack
            justifyContent="center"
            alignItems="center"
            sx={{
              width: "128px",
              height: "128px",
              marginRight: "32px",
              borderRadius: "8px",
              overflow: "hidden",
              background:
                "linear-gradient(to bottom right, #C6FFDD 0%, #FBD786 50%, #F7797D 100%)",
            }}
          >
            <ArtistThumbnail artist={artist} />
          </Stack>
          <Box>
            <Typography variant="h4">{artist.name}</Typography>
            <Typography>
              {pluralize("media", artistVideos.length, true)}
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
        <VirtualizedMediaList videos={artistVideos} />
      </Box>
    </Stack>
  );
});

export default ArtistPage;
