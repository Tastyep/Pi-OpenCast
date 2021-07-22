import React from "react";
import { Grid, Slider, Tooltip } from "@material-ui/core";

import VolumeDown from "@material-ui/icons/VolumeDown";
import VolumeUp from "@material-ui/icons/VolumeUp";

import playerAPI from "services/api/player";
import { useAppStore } from "./app_context";
import { observer } from "mobx-react-lite";

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

  const handleCommit = (_, value) => {
    playerAPI.updateVolume(value);
  };

  return (
    <div>
      <Grid container spacing={2}>
        <Grid item>
          <VolumeDown />
        </Grid>
        <Grid item xs>
          <Slider
            value={store.player.volume ? store.player.volume : 50}
            ValueLabelComponent={ValueLabelComponent}
            onChange={(_, value) => {
              store.player.setVolume(value);
            }}
            onChangeCommitted={handleCommit}
            aria-labelledby="continuous-slider"
          />
        </Grid>
        <Grid item>
          <VolumeUp />
        </Grid>
      </Grid>
    </div>
  );
});

export default VolumeControl;
