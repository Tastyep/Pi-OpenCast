import React from "react";
import { ButtonGroup, Grid, IconButton } from "@mui/material";
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

import VolumeControl from "components/volume_control";

import playerAPI from "services/api/player";

import "./player_control.css";
import { useAppStore } from "./app_context";
import { observer } from "mobx-react-lite";

const BarContainer = styled("div")({
  display: "flex",
  background: "#858585",
  alignItems: "center",
  height: "80px",
});

const ControlBar = observer(() => {
  const store = useAppStore();

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
    <BarContainer>
      <IconButton
        size="medium"
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
      <IconButton
        onClick={() => updatePlayer(playerAPI.seekMedia, false, true)}
      >
        <FastRewindIcon />
      </IconButton>
      <IconButton
        onClick={() => updatePlayer(playerAPI.seekMedia, false, false)}
      >
        <ArrowLeftIcon />
      </IconButton>
      <IconButton
        onClick={() => updatePlayer(playerAPI.seekMedia, true, false)}
      >
        <ArrowRightIcon />
      </IconButton>
      <IconButton onClick={() => updatePlayer(playerAPI.seekMedia, true, true)}>
        <FastForwardIcon />
      </IconButton>

      <img
        src={activeVideo.thumbnail}
        alt={activeVideo.title}
        style={{ maxHeight: "80%" }}
      />
      <div style={{ marginLeft: "8px" }}>
        {activeVideo.title}
        <br />
        {activeVideo.title}
      </div>

      <VolumeControl />
      <ButtonGroup size="small" variant="text">
        <IconButton onClick={() => updatePlayer(playerAPI.seekSubtitle, false)}>
          <RemoveCircleOutlineIcon />
        </IconButton>
        <IconButton onClick={() => updatePlayer(playerAPI.toggleSubtitle)}>
          <ClosedCaptionIcon />
        </IconButton>
        <IconButton onClick={() => updatePlayer(playerAPI.seekSubtitle, true)}>
          <AddCircleOutlineIcon />
        </IconButton>
      </ButtonGroup>
    </BarContainer>
  );
});

export default ControlBar;
