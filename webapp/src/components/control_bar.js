import React from "react";
import { ButtonGroup, Grid, IconButton } from "@material-ui/core";
import { makeStyles, createStyles } from "@material-ui/core/styles";

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

import VolumeControl from "components/volume_control";

import playerAPI from "services/api/player";

import "./player_control.css";
import { useAppStore } from "./app_context";
import { observer } from "mobx-react-lite";

const useStyles = makeStyles(() =>
  createStyles({
    bar: {
      display: "flex",
      background: "#858585",
      alignItems: "center",
      height: "80px",
    },
    videoThumbnail: {
      maxHeight: "80%",
    },
    videoInfo: {
      marginLeft: "8px",
    },
  })
);

const ControlBar = observer(() => {
  const store = useAppStore();
  const classes = useStyles();
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
    <div className={classes.bar}>
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
        className={classes.videoThumbnail}
      />
      <div className={classes.videoInfo}>
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
    </div>
  );
});

export default ControlBar;
