import React, { useEffect } from "react";
import { Grid, Typography, Slider } from "@material-ui/core";

import VolumeDown from "@material-ui/icons/VolumeDown";
import VolumeUp from "@material-ui/icons/VolumeUp";

import playerAPI from "services/api/player";

function VolumeControl() {
  const [value, setValue] = React.useState(30);

  const handleChange = (event, newValue) => {
    setValue(newValue);
  };

  const setPlayerVolume = (player) => {
    setValue(player.volume);
  };

  const handleCommit = (event, newValue) => {
    playerAPI.updateVolume(newValue);
  };

  useEffect(() => {
    playerAPI
      .get()
      .then((response) => {
        setPlayerVolume(response.data);
      })
      .catch((error) => console.log(error));
  }, []);

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
