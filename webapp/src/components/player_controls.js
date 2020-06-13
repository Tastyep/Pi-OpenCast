import React from "react";
import { IconButton, ButtonGroup, Grid } from "@material-ui/core";

import PauseOutlinedIcon from "@material-ui/icons/PauseOutlined";
import StopOutlinedIcon from "@material-ui/icons/StopOutlined";
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
  // Highlight subtitle button when on
  return (
    <Grid container spacing={1}>
      <Grid item xs={6} md={4}>
        <ButtonGroup size="small" variant="text">
          <IconButton onClick={() => player.prevMedia()}>
            <SkipPreviousIcon />
          </IconButton>
          <IconButton onClick={() => player.pauseMedia()}>
            <PauseOutlinedIcon />
          </IconButton>
          <IconButton onClick={() => player.stopMedia()}>
            <StopOutlinedIcon />
          </IconButton>
          <IconButton onClick={() => player.nextMedia()}>
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
