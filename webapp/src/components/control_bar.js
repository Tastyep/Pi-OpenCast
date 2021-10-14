import React, { useState } from "react";
import { Collapse, IconButton, Stack, Typography } from "@mui/material";
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

import Media from "react-media";
import { SIZES } from "constants.js";

import VolumeControl from "components/volume_control";

import playerAPI from "services/api/player";

import "./player_control.css";
import { useAppStore } from "./app_context";
import { observer } from "mobx-react-lite";

const BarContainer = styled(Stack)({
  background: "#F2F2F2",
  alignItems: "center",
  flexDirection: "row",
  justifyContent: "space-between",
  height: "48px",
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
      .catch((error) => console.log(error));
  };

  // Highlight subtitle button when on
  return (
    <Media queries={{ large: { minWidth: SIZES.large.min } }}>
      {(matches) =>
        matches.large ? (
          <BarContainer direction="row">
            <div>
              <IconButton size="small" onClick={() => {}}>
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
              <IconButton size="small" onClick={() => {}}>
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
            </div>

            <Stack
              direction="row"
              alignItems="center"
              style={{ height: "100%" }}
            >
              <img
                src={activeVideo.thumbnail}
                alt={activeVideo.title}
                style={{ height: "100%" }}
              />
              <div style={{ marginLeft: "8px" }}>
                <Typography> {activeVideo.title}</Typography>
                <Typography>{"Artist • Album • Date"}</Typography>
              </div>
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
              root={{ height: 200 }}
              sx={{
                minHeight: "auto",
              }}
            >
              <BarContainer>
                <div>
                  <IconButton
                    size="small"
                    onClick={() =>
                      updatePlayer(playerAPI.seekMedia, false, true)
                    }
                    sx={{ marginLeft: "16px" }}
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
                </div>
                <div>
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
                </div>
                <VolumeControl />
              </BarContainer>
            </Collapse>
            <BarContainer direction="row">
              <Stack
                direction="row"
                alignItems="center"
                style={{ height: "100%" }}
              >
                <img
                  src={activeVideo.thumbnail}
                  alt={activeVideo.title}
                  style={{ height: "100%" }}
                />
                <div
                  style={{
                    display: "flex",
                    flexDirection: "column",
                    marginLeft: "8px",
                  }}
                >
                  <Typography variant="body2">{activeVideo.title} </Typography>
                  <Typography variant="caption">
                    {"Artist • Album • Date"}
                  </Typography>
                </div>
              </Stack>
              <div style={{ display: "flex" }}>
                <IconButton size="small" onClick={() => {}}>
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
                <IconButton size="small" onClick={() => {}}>
                  <SkipNextIcon />
                </IconButton>
              </div>
              <IconButton size="small" onClick={() => setExpanded(!expanded)}>
                {expanded ? <ExpandLessIcon /> : <ExpandMoreIcon />}
              </IconButton>
            </BarContainer>
          </div>
        )
      }
    </Media>
  );
});

export default ControlBar;
