import React from 'react'
import { Button, ButtonGroup, Grid } from "@material-ui/core";

import PauseIcon from "@material-ui/icons/Pause";
import PlayArrowIcon from "@material-ui/icons/PlayArrow";
import StopIcon from "@material-ui/icons/Stop";
import ClosedCaptionIcon from "@material-ui/icons/ClosedCaption";
import AddCircleOutlineIcon from "@material-ui/icons/AddCircleOutline";
import RemoveCircleOutlineIcon from "@material-ui/icons/RemoveCircleOutline";
import FastRewindIcon from "@material-ui/icons/FastRewind";
import FastForwardIcon from "@material-ui/icons/FastForward";
import ArrowLeftIcon from "@material-ui/icons/ArrowLeft";
import ArrowRightIcon from "@material-ui/icons/ArrowRight";

import playerAPI from "services/api/player";

import "./player_control.css";
import { useAppStore } from "./app_context";
import { observer } from "mobx-react-lite";

const PlayerControls = observer(() => {
  const store = useAppStore() 

  const updatePlayer = (update, ...args) => {
    update(...args)
      .then((response) => {
        store.loadPlayer()
      })
      .catch((error) => console.log(error));
  }

  // Highlight subtitle button when on
  return (
    <Grid container spacing={1}>
      <Grid item xs={6} md={4}>
        <ButtonGroup size="small" variant="text">
          <Button onClick={() => updatePlayer(playerAPI.pauseMedia)}>
            {store.player.state !== "PAUSED" ? <PauseIcon /> : <PlayArrowIcon />}
          </Button>
          <Button onClick={() => updatePlayer(playerAPI.stopMedia)}>
            <StopIcon />
          </Button>
        </ButtonGroup>
      </Grid>
      <Grid item xs={6} md={4} className="SeekButtons">
        <ButtonGroup size="small" variant="text">
          <Button
            onClick={() => updatePlayer(playerAPI.seekMedia, false, true)}
          >
            <FastRewindIcon />
          </Button>
          <Button
            onClick={() => updatePlayer(playerAPI.seekMedia, false, false)}
          >
            <ArrowLeftIcon />
          </Button>
          <Button
            onClick={() => updatePlayer(playerAPI.seekMedia, true, false)}
          >
            <ArrowRightIcon />
          </Button>
          <Button
            onClick={() => updatePlayer(playerAPI.seekMedia, true, true)}
          >
            <FastForwardIcon />
          </Button>
        </ButtonGroup>
      </Grid>
      <Grid item xs={12} md={4} className="SubtitleButtons">
        <ButtonGroup size="small" variant="text">
          <Button
            onClick={() => updatePlayer(playerAPI.seekSubtitle, false)}
          >
            <RemoveCircleOutlineIcon />
          </Button>
          <Button onClick={() => updatePlayer(playerAPI.toggleSubtitle)}>
            <ClosedCaptionIcon />
          </Button>
          <Button
            onClick={() => updatePlayer(playerAPI.seekSubtitle, true)}
          >
            <AddCircleOutlineIcon />
          </Button>
        </ButtonGroup>
      </Grid>
    </Grid>
  );
})

export default PlayerControls;
