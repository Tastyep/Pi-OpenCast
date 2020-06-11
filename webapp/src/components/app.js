import React, { Component } from "react";

import Header from "./header";
import StreamInput from "./stream_input";
import PlayerControls from "./player_controls";
import VolumeControl from "./volume_control";
import { Grid } from "@material-ui/core";

class App extends Component {
  render() {
    return (
      <Grid container>
        <Grid item xs={false} sm={2} md={3} />
        <Grid item container direction="column" xs={12} sm={8} md={6}>
          <Grid item>
            <Header />
          </Grid>
          <Grid item>
            <StreamInput />
          </Grid>
          <Grid item>
            <VolumeControl />
          </Grid>
          <Grid item>
            <PlayerControls />
          </Grid>
        </Grid>
        <Grid item xs={false} sm={2} md={3} />
      </Grid>
    );
  }
}

export default App;
