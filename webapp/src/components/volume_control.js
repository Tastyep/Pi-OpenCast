import React from "react";
import { Grid, Typography, Slider } from "@material-ui/core";

import VolumeDown from "@material-ui/icons/VolumeDown";
import VolumeUp from "@material-ui/icons/VolumeUp";

import player from "services/api/player";

function VolumeControl() {
  const [value, setValue] = React.useState(30);

  const handleChange = (event, newValue) => {
    setValue(newValue);
  };

  const handleCommit = (event, newValue) => {
    player.updateVolume(newValue);
  };

  return (
    <div>
      <Typography id="continuous-slider" gutterBottom>
        Volume {value} %
      </Typography>
      <Grid container spacing={2}>
        <Grid item>
          <VolumeDown />
        </Grid>
        <Grid item xs>
          <Slider
            value={value}
            onChange={handleChange}
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
}

export default VolumeControl;