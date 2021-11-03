import React, { useState } from "react";
import { Collapse, Grid, IconButton, Stack, Typography } from "@mui/material";
import { styled } from "@mui/material/styles";

import PauseIcon from "@mui/icons-material/Pause";
import PlayArrowIcon from "@mui/icons-material/PlayArrow";
import StopIcon from "@mui/icons-material/Stop";
import ClosedCaptionIcon from "@mui/icons-material/ClosedCaption";
import AddCircleOutlineIcon from "@mui/icons-material/AddCircleOutline";
import RemoveCircleOutlineIcon from "@mui/icons-material/RemoveCircleOutline";
import FastRewindIcon from "@mui/icons-material/FastRewind";
import FastForwardIcon from "@mui/icons-material/FastForward";
import ArrowLeftIcon from "@mui/icons-material/ArrowLeft";
import ArrowRightIcon from "@mui/icons-material/ArrowRight";
import SkipNextIcon from "@mui/icons-material/SkipNext";
import SkipPreviousIcon from "@mui/icons-material/SkipPrevious";
import ExpandLessIcon from "@mui/icons-material/ExpandLess";
import ExpandMoreIcon from "@mui/icons-material/ExpandMore";

import MediaQuery from "react-responsive";
import { SIZES } from "constants.js";

import VolumeControl from "components/volume_control";

import playerAPI from "services/api/player";
import snackBarHandler from "services/api/error";

import "./player_control.css";
import { useAppStore } from "./app_context";
import { observer } from "mobx-react-lite";

const BarContainer = styled(Stack)({
  backgroundColor: "#F2F2F2",
  alignItems: "center",
  flexDirection: "row",
  justifyContent: "space-between",
  height: "56px",
  overflow: "clip",
});

const ControlBar = observer(() => {
  const store = useAppStore();
  const [expanded, setExpanded] = useState(false);

  const activeVideo = store.videos[store.player.videoId];

  if (!activeVideo) {
    return null;
  }

  const updatePlayer = (update, ...args) => {
    update(...args)
      .then((response) => {
        store.loadPlayer();
      })
      .catch(snackBarHandler(store));
  };

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

  // Highlight subtitle button when on
  return (
    <MediaQuery minWidth={SIZES.large.min}>
      {(matches) =>
        matches ? (
          <BarContainer direction="row">
            <Stack direction="row">
              <IconButton size="small" onClick={playPrev}>
                <SkipPreviousIcon />
              </IconButton>
              <IconButton
                size="small"
                onClick={() => updatePlayer(playerAPI.pauseMedia)}
              >
                {store.player.state !== "PAUSED" ? (
                  <PauseIcon fontSize="large" />
                ) : (
                  <PlayArrowIcon fontSize="large" />
                )}
              </IconButton>
              <IconButton
                size="small"
                disableFocusRipple
                disableRipple
                onClick={() => updatePlayer(playerAPI.stopMedia)}
              >
                <StopIcon />
              </IconButton>
              <IconButton size="small" onClick={playNext}>
                <SkipNextIcon />
              </IconButton>

              <IconButton
                size="small"
                onClick={() => updatePlayer(playerAPI.seekMedia, false, true)}
                sx={{ marginLeft: "16px" }}
              >
                <FastRewindIcon />
              </IconButton>
              <IconButton
                size="small"
                onClick={() => updatePlayer(playerAPI.seekMedia, false, false)}
              >
                <ArrowLeftIcon />
              </IconButton>
              <IconButton
                size="small"
                onClick={() => updatePlayer(playerAPI.seekMedia, true, false)}
              >
                <ArrowRightIcon />
              </IconButton>
              <IconButton
                size="small"
                onClick={() => updatePlayer(playerAPI.seekMedia, true, true)}
              >
                <FastForwardIcon />
              </IconButton>
            </Stack>

            <Stack
              direction="row"
              alignItems="center"
              sx={{
                height: "100%",
                minWidth: "0px",
                margin: "0px 16px",
                overflow: "hidden",
              }}
            >
              <img
                src={activeVideo.thumbnail}
                alt={activeVideo.title}
                style={{ height: "100%" }}
              />
              <Stack
                sx={{
                  marginLeft: "8px",
                  minWidth: "0px",
                  overflow: "hidden",
                }}
              >
                <Typography noWrap> {activeVideo.title}</Typography>
                <Typography>
                  {activeVideo.album || "Artist • Album • Date"}
                </Typography>
              </Stack>
            </Stack>

            <Stack direction="row">
              <VolumeControl />
              <IconButton
                size="small"
                onClick={() => updatePlayer(playerAPI.seekSubtitle, false)}
              >
                <RemoveCircleOutlineIcon />
              </IconButton>
              <IconButton
                size="small"
                onClick={() => updatePlayer(playerAPI.toggleSubtitle)}
              >
                <ClosedCaptionIcon />
              </IconButton>
              <IconButton
                size="small"
                onClick={() => updatePlayer(playerAPI.seekSubtitle, true)}
              >
                <AddCircleOutlineIcon />
              </IconButton>
            </Stack>
          </BarContainer>
        ) : (
          <div style={{ minHeight: "auto" }}>
            <Collapse
              in={expanded}
              timeout="auto"
              unmountOnExit
              sx={{
                minHeight: "auto",
              }}
            >
              <Grid
                container
                sx={{ paddingBottom: "8px", backgroundColor: "#F2F2F2" }}
              >
                <Grid item xs={12} sx={{ paddingLeft: "8px" }}>
                  <VolumeControl />
                </Grid>
                <Grid item xs={6}>
                  <IconButton
                    size="small"
                    onClick={() =>
                      updatePlayer(playerAPI.seekMedia, false, true)
                    }
                  >
                    <FastRewindIcon />
                  </IconButton>
                  <IconButton
                    size="small"
                    onClick={() =>
                      updatePlayer(playerAPI.seekMedia, false, false)
                    }
                  >
                    <ArrowLeftIcon />
                  </IconButton>
                  <IconButton
                    size="small"
                    disableFocusRipple
                    disableRipple
                    onClick={() => updatePlayer(playerAPI.stopMedia)}
                  >
                    <StopIcon />
                  </IconButton>
                  <IconButton
                    size="small"
                    onClick={() =>
                      updatePlayer(playerAPI.seekMedia, true, false)
                    }
                  >
                    <ArrowRightIcon />
                  </IconButton>
                  <IconButton
                    size="small"
                    onClick={() =>
                      updatePlayer(playerAPI.seekMedia, true, true)
                    }
                  >
                    <FastForwardIcon />
                  </IconButton>
                </Grid>
                <Grid item container xs={6} justifyContent="flex-end">
                  <IconButton
                    size="small"
                    onClick={() => updatePlayer(playerAPI.seekSubtitle, false)}
                  >
                    <RemoveCircleOutlineIcon />
                  </IconButton>
                  <IconButton
                    size="small"
                    onClick={() => updatePlayer(playerAPI.toggleSubtitle)}
                  >
                    <ClosedCaptionIcon />
                  </IconButton>
                  <IconButton
                    size="small"
                    onClick={() => updatePlayer(playerAPI.seekSubtitle, true)}
                  >
                    <AddCircleOutlineIcon />
                  </IconButton>
                </Grid>
              </Grid>
            </Collapse>
            <BarContainer direction="row">
              <Stack
                direction="row"
                alignItems="center"
                style={{ height: "100%", minWidth: "0px" }}
              >
                <img
                  src={activeVideo.thumbnail}
                  alt={activeVideo.title}
                  style={{
                    height: "100%",
                    aspectRatio: "1/1",
                    objectFit: "cover",
                  }}
                />
                <Stack
                  sx={{
                    marginLeft: "8px",
                    minWidth: "0px",
                    overflow: "hidden",
                  }}
                >
                  <Typography noWrap variant="body2">
                    {activeVideo.title}
                  </Typography>
                  <Typography variant="caption">
                    {activeVideo.album || "Artist • Album • Date"}
                  </Typography>
                </Stack>
              </Stack>
              <Stack direction="row">
                <IconButton size="small" onClick={playPrev}>
                  <SkipPreviousIcon />
                </IconButton>
                <IconButton
                  size="small"
                  onClick={() => updatePlayer(playerAPI.pauseMedia)}
                >
                  {store.player.state !== "PAUSED" ? (
                    <PauseIcon fontSize="large" />
                  ) : (
                    <PlayArrowIcon fontSize="large" />
                  )}
                </IconButton>
                <IconButton size="small" onClick={playNext}>
                  <SkipNextIcon />
                </IconButton>
                <IconButton size="small" onClick={() => setExpanded(!expanded)}>
                  {expanded ? <ExpandMoreIcon /> : <ExpandLessIcon />}
                </IconButton>
              </Stack>
            </BarContainer>
          </div>
        )
      }
    </MediaQuery>
  );
});

export default ControlBar;
