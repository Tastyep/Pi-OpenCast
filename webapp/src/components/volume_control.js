import React, { useState } from "react";
import { Grid, Slider, Tooltip, Button } from "@material-ui/core";
import { makeStyles, createStyles } from "@material-ui/core/styles";
import VolumeUp from "@material-ui/icons/VolumeUp";
import VolumeOff from "@material-ui/icons/VolumeOff";

import playerAPI from "services/api/player";
import { useAppStore } from "./app_context";
import { observer } from "mobx-react-lite";

const useStyles = makeStyles(() =>
  createStyles({
    container: {},
  })
);

function ValueLabelComponent(props) {
  const { children, open, value } = props;

  return (
    <Tooltip open={open} enterTouchDelay={0} placement="top" title={value}>
      {children}
    </Tooltip>
  );
}

const VolumeControl = observer(() => {
  const store = useAppStore();
  const [sliderDisplay, setSliderDisplay] = useState(false);
  const [oldVolume, setOldVolume] = useState(store.player.volume);
  const classes = useStyles();

  const handleCommit = (_, value) => {
    playerAPI.updateVolume(value);
  };

  const handleClick = () => {
    if (store.player.volume === 0) {
      store.player.setVolume(oldVolume);
      playerAPI.updateVolume(oldVolume);
      return;
    }
    setOldVolume(store.player.volume);
    store.player.setVolume(0);
    playerAPI.updateVolume(0);
  };

  return (
    <Grid
      container
      onMouseEnter={() => {
        setSliderDisplay(true);
      }}
      onMouseLeave={() => {
        setSliderDisplay(false);
      }}
      className={classes.container}
    >
      <Grid item xs={10}>
        {sliderDisplay && (
          <Slider
            value={store.player.volume}
            ValueLabelComponent={ValueLabelComponent}
            onChange={(_, value) => {
              store.player.setVolume(value);
            }}
            onChangeCommitted={handleCommit}
            aria-labelledby="continuous-slider"
          />
        )}
      </Grid>
      <Grid item xs={2}>
        <Button onClick={handleClick}>
          {(store.player.volume === 0 && <VolumeOff />) || <VolumeUp />}
        </Button>
      </Grid>
    </Grid>
  );
});

export default VolumeControl;
