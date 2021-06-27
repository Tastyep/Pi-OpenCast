import React, { useEffect } from "react";

import { Grid, Paper } from "@material-ui/core";

import Header from "./header";
import StreamInput from "./stream_input";
import VideoList from "./video_list";
import PlayerControls from "./player_controls";
import VolumeControl from "./volume_control";
import { useAppStore } from "./app_context";

function App() {
  const store = useAppStore()

  useEffect(() => {
    store.load()
  }, [store]);

  return (
    <Grid container>
      <Grid item sm={1} md={2} />
      <Grid item container xs={12} sm={10} md={8}>
        <Grid
          item
          container
          style={{ display: "block", position: "relative" }}
        >
          <Header />
          <Paper elevation={3} style={{ flex: 1, padding: 24 }}>
            <Grid
              item
              container
              direction="column"
              spacing={4}
              style={{ display: "block" }}
            >
              <Grid item>
                <StreamInput />
              </Grid>
              <Grid item>
                <VideoList />
              </Grid>
              <Grid item>
                <PlayerControls />
              </Grid>
              <Grid item>
                <VolumeControl />
              </Grid>
            </Grid>
          </Paper>
        </Grid>
      </Grid>
      <Grid item sm={1} md={2} />
    </Grid>
  )
}

export default App;
