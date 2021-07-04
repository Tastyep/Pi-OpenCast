import React from "react";
import { Grid, Typography, Slider } from "@material-ui/core";

import VolumeDown from "@material-ui/icons/VolumeDown";
import VolumeUp from "@material-ui/icons/VolumeUp";

import playerAPI from "services/api/player";
import { useAppStore } from "./app_context";
import { observer } from "mobx-react-lite";

const VolumeControl = observer(() => {
  const store = useAppStore();

  const handleCommit = (_, value) => {
    playerAPI.updateVolume(value);
  };

  const generateMarks = () => {
    return [
      {
        value: store.player.volume,
        label: store.player.volume + "%",
      },
    ];
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
            onChange={(_, value) => {
              store.player.setVolume(value);
            }}
            onChangeCommitted={handleCommit}
            marks={generateMarks()}
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
