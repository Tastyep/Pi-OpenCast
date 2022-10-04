import React, { useState } from "react";
import {
  Box,
  IconButton,
  Stack,
  Typography,
} from "@mui/material";

import ListItemText from "@mui/material/ListItemText";
import ListItemIcon from "@mui/material/ListItemIcon";
import Menu from "@mui/material/Menu";
import MenuItem from "@mui/material/MenuItem";

import StopIcon from "@mui/icons-material/Stop";
import ClosedCaptionIcon from "@mui/icons-material/ClosedCaption";
import ClosedCaptionDisabledIcon from "@mui/icons-material/ClosedCaptionDisabled";
import AddCircleOutlineIcon from "@mui/icons-material/AddCircleOutline";
import RemoveCircleOutlineIcon from "@mui/icons-material/RemoveCircleOutline";
import SkipNextIcon from "@mui/icons-material/SkipNext";
import SkipPreviousIcon from "@mui/icons-material/SkipPrevious";
import ExpandLessIcon from "@mui/icons-material/ExpandLess";
import PauseCircleFilledIcon from "@mui/icons-material/PauseCircleFilled";
import PlayCircleFilledIcon from "@mui/icons-material/PlayCircleFilled";
import MoreVertIcon from '@mui/icons-material/MoreVert';

import VolumeControl from "components/volume_control";
import PlayerProgress from "components/player_progress";

import { durationToHMS, countHMSParts } from "services/duration";
import playerAPI from "services/api/player";
import snackBarHandler from "services/api/error";

import { useAppStore } from "components/app_context";
import { observer } from "mobx-react-lite";

const updatePlayer = (store, update, ...args) => {
  update(...args).catch(snackBarHandler(store));
};

const PausePlayIcon = observer(() => {
  const store = useAppStore();
  const isPlayerPlaying = store.player.isPlaying;

  const iconStyle = { minWidth: "64px", minHeight: "64px" };

  return (
    <IconButton
      size="large"
      disableRipple={true}
      onClick={() => updatePlayer(store, playerAPI.pauseMedia)}
      sx={{ color: "rgba(89,123,157,0.87)" }}
    >
      {isPlayerPlaying ? (
        <PauseCircleFilledIcon fontSize="large" style={iconStyle} />
      ) : (
        <PlayCircleFilledIcon fontSize="large" style={iconStyle} />
      )}
    </IconButton>
  );
});

const SubtitleControl = observer(() => {
  const store = useAppStore();

  return (
    <>
      <IconButton
        size="small"
        onClick={() =>
          updatePlayer(
            store,
            playerAPI.seekSubtitle,
            store.player.subDelay - 100
          )
        }
      >
        <RemoveCircleOutlineIcon />
      </IconButton>
      <IconButton
        size="small"
        onClick={() => updatePlayer(store, playerAPI.toggleSubtitle)}
      >
        {store.player.subState ? (
          <ClosedCaptionIcon />
        ) : (
          <ClosedCaptionDisabledIcon />
        )}
      </IconButton>
      <IconButton
        size="small"
        onClick={() =>
          updatePlayer(
            store,
            playerAPI.seekSubtitle,
            store.player.subDelay + 100
          )
        }
      >
        <AddCircleOutlineIcon />
      </IconButton>
    </>
  );
});

const OptionMenu = (props) => {
  const store = useAppStore();
  const { open, anchorEl, closeMenu, closeParent } = props;

  const stop = () => {
    playerAPI
      .stopMedia()
      .catch(snackBarHandler(store));
    closeMenu();
    closeParent();
  };


  return (
    <Menu
      id="option-menu"
      anchorEl={anchorEl}
      open={open}
      onClose={closeMenu}
      MenuListProps={{
        "aria-labelledby": "basic-button",
      }}
      transformOrigin={{ horizontal: "right", vertical: "top" }}
      anchorOrigin={{ horizontal: "right", vertical: "bottom" }}
    >
      <MenuItem onClick={stop}>
        <ListItemIcon>
          <StopIcon />
        </ListItemIcon>
        <ListItemText>Stop</ListItemText>
      </MenuItem>
    </Menu>
  );
};

const PlayingMediaImage = (props) => {
  const { src, alt } = props;

  return (
    <Box
      justifyContent="center"
      alignItems="center"
      sx={{ display: "flex", backgroundColor: "black", width: "100%", height: "50vh", position: "relative" }}
    >
      <img
        src={src}
        alt={alt}
        style={{
          height: "100%",
          width: "100%",
          objectFit: "cover",
          filter: "blur(0.12rem)",
        }}
      />
      <img
        src={src}
        alt={alt}
        style={{
          position: "absolute",
          height: "65%",
          aspectRatio: "1 / 1",
          objectFit: "cover",
          borderRadius: "100%",
          borderWidth: "large",
          borderStyle: "solid",
          borderColor: "rgba(255,255,255,0.2)",
        }}
      />
    </Box>
  );
};

const ControlPage = observer((props) => {
  const store = useAppStore();

  const { closePage } = props;
  const activeVideo = store.videos[store.player.videoId];

  const [anchor, setAnchor] = useState(null);
  const isMenuOpen = Boolean(anchor);

  if (!activeVideo) {
    return null;
  }

  const activeArtist = store.artists[activeVideo.artist_id];
  const activeAlbum = store.albums[activeVideo.album_id];

  const playNext = () => {
    if (!activeVideo) {
      store.enqueueSnackbar({
        message: "no active media",
        options: {
          variant: "error",
        },
      });
      return;
    }

    const playlist = store.playerPlaylist;
    const idx = playlist.ids.indexOf(activeVideo.id);

    if (idx + 1 === playlist.ids.length) {
      store.enqueueSnackbar({
        message: "no more media available",
        options: {
          variant: "error",
        },
      });
      return;
    }

    playerAPI.playMedia(playlist.ids[idx + 1]).catch(snackBarHandler(store));
  };

  const playPrev = () => {
    if (!activeVideo) {
      store.enqueueSnackbar({
        message: "no active media",
        options: {
          variant: "error",
        },
      });
      return;
    }

    const playlist = store.playerPlaylist;
    const idx = playlist.ids.indexOf(activeVideo.id);

    if (idx - 1 < 0) {
      store.enqueueSnackbar({
        message: "no more media available",
        options: {
          variant: "error",
        },
      });
      return;
    }

    playerAPI.playMedia(playlist.ids[idx - 1]).catch(snackBarHandler(store));
  };

  const iconStyle = { minWidth: "40px", minHeight: "40px" };

  // Highlight subtitle button when on
  return (
    <Stack
      alignItems="center"
      sx={{ position: "relative", height: "100vh" }}
    >
      <Stack direction="row" justifyContent="space-between" alignItems="center" sx={{ backgroundColor: "#F2F2F2", width: "100%" }}>
        <IconButton size="large" onClick={() => closePage()}>
          <ExpandLessIcon fontSize="medium" />
        </IconButton>
        <Typography noWrap align="center" noWrap sx={{ height: "auto" }}>
          {activeVideo.title}
        </Typography>
        <IconButton
          size="large"
          aria-expanded={isMenuOpen ? "true" : undefined}
          onClick={(e) => setAnchor(e.currentTarget)}
        >
          <MoreVertIcon fontSize="medium" />
        </IconButton>
        <OptionMenu
          open={isMenuOpen}
          anchorEl={anchor}
          closeMenu={() => setAnchor(null)}
          closeParent={closePage}
        />
      </Stack>

      <PlayingMediaImage src={activeVideo.thumbnail} alt={activeVideo.title} />

      <Stack alignItems="center" style={{ width: "88%", flex: 1 }}>
        <Box sx={{ marginTop: "24px", width: "100%" }}>
          <PlayerProgress height={6} />
          <Stack
            direction="row"
            justifyContent="space-between"
            style={{ marginTop: "16px", marginBottom: "8px" }}
          >
            <Typography>
              {durationToHMS(activeVideo.playTime, countHMSParts(activeVideo.duration * 1000))}
            </Typography>
            <Typography>
              {durationToHMS(activeVideo.duration * 1000)}
            </Typography>
          </Stack>
        </Box>
        <Stack
          direction="column"
          justifyContent="center"
          style={{ margin: "0px 0px", width: "100%" }}
        >
          <Typography noWrap align="center" variant="h5">
            {activeVideo.title}
          </Typography>
          {activeArtist && (
            <Typography noWrap align="center">
              From {activeArtist.name}
            </Typography>
          )}
        </Stack>
        <Stack
          direction="row"
          justifyContent="space-around"
          alignItems="center"
          sx={{ width: "70%", flex: 1 }}
        >
          <IconButton disableRipple={true} size="medium" onClick={playPrev}>
            <SkipPreviousIcon fontSize="inherit" style={iconStyle} />
          </IconButton>
          <PausePlayIcon />
          <IconButton disableRipple={true} size="medium" onClick={playNext}>
            <SkipNextIcon fontSize="inherit" style={iconStyle} />
          </IconButton>
        </Stack>

        <Box style={{ width: "100%" }}>
          <VolumeControl />
        </Box>
      </Stack>
    </Stack>
  );
});

export default ControlPage;
