import React, { useState, useEffect } from "react";
import { IconButton, ButtonGroup, Grid } from "@material-ui/core";

import PauseIcon from "@material-ui/icons/Pause";
import PlayArrowIcon from "@material-ui/icons/PlayArrow";
import StopIcon from "@material-ui/icons/Stop";
import SkipNextIcon from "@material-ui/icons/SkipNext";
import SkipPreviousIcon from "@material-ui/icons/SkipPrevious";
import ClosedCaptionIcon from "@material-ui/icons/ClosedCaption";
import AddCircleOutlineIcon from "@material-ui/icons/AddCircleOutline";
import RemoveCircleOutlineIcon from "@material-ui/icons/RemoveCircleOutline";
import FastRewindIcon from "@material-ui/icons/FastRewind";
import FastForwardIcon from "@material-ui/icons/FastForward";
import ArrowLeftIcon from "@material-ui/icons/ArrowLeft";
import ArrowRightIcon from "@material-ui/icons/ArrowRight";

import player from "services/api/player";

import "./player_control.css";

function PlayerControls() {
  const [pauseStatus, setPauseStatus] = useState(true);

  const updatePlayerState = (player) => {
    if (player.status === "PAUSED") {
      setPauseStatus(false);
    } else {
      setPauseStatus(true);
    }
  };

  useEffect(() => {
    player
      .get()
      .then((response) => {
        updatePlayerState(response.data);
      })
      .catch((error) => console.log(error));
  });

  // Highlight subtitle button when on
  return (
    <Grid container spacing={1}>
      <Grid item xs={6} md={4}>
        <ButtonGroup size="small" variant="text">
          <IconButton onClick={() => player.pickMedia(undefined)}>
            <SkipPreviousIcon />
          </IconButton>
          <IconButton onClick={() => player.pauseMedia()}>
            {pauseStatus ? <PauseIcon /> : <PlayArrowIcon />}
          </IconButton>
          <IconButton onClick={() => player.stopMedia()}>
            <StopIcon />
          </IconButton>
          <IconButton onClick={() => player.pickMedia(undefined)}>
            <SkipNextIcon />
          </IconButton>
        </ButtonGroup>
      </Grid>
      <Grid item xs={6} md={4} className="SeekButtons">
        <ButtonGroup size="small" variant="text">
          <IconButton onClick={() => player.seekMedia(false, true)}>
            <FastRewindIcon />
          </IconButton>
          <IconButton onClick={() => player.seekMedia(false, false)}>
            <ArrowLeftIcon />
          </IconButton>
          <IconButton onClick={() => player.seekMedia(true, false)}>
            <ArrowRightIcon />
          </IconButton>
          <IconButton onClick={() => player.seekMedia(true, true)}>
            <FastForwardIcon />
          </IconButton>
        </ButtonGroup>
      </Grid>
      <Grid item xs={12} md={4} className="SubtitleButtons">
        <ButtonGroup size="small" variant="text">
          <IconButton onClick={() => player.seekSubtitle(false)}>
            <RemoveCircleOutlineIcon />
          </IconButton>
          <IconButton onClick={() => player.toggleSubtitle()}>
            <ClosedCaptionIcon />
          </IconButton>
          <IconButton onClick={() => player.seekSubtitle(true)}>
            <AddCircleOutlineIcon />
          </IconButton>
        </ButtonGroup>
      </Grid>
    </Grid>
  );
}

export default PlayerControls;
