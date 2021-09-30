import React, { useEffect } from "react";

import { Grid, Paper } from "@material-ui/core";
import { makeStyles, createStyles } from "@material-ui/core/styles";

import HomePage from "views/home"

import Header from "components/header";
import StreamInput from "components/stream_input";
import PlayerControls from "components/player_controls";
import VolumeControl from "components/volume_control";
import Playlists from "components/playlists";
import { useAppStore } from "components/app_context";

const useStyles = makeStyles(() =>
  createStyles({
    root: {
      width: "100%",
      backgroundColor: "#F5F5F5",
    },
  })
);

function App() {
  const store = useAppStore();
  const classes = useStyles();

  useEffect(() => {
    store.load();
  }, [store]);

  return (
    <Grid container className={classes.root}>
      <Grid item sm={1} md={2} />
      <Grid item container xs={12} sm={10} md={8}>
        <Grid item container style={{ display: "block", position: "relative" }}>
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
                <HomePage />
              </Grid>
              <Grid item>
                <PlayerControls />
              </Grid>
              <Grid item>
                <VolumeControl />
              </Grid>
              <Grid item>
                <Playlists />
              </Grid>
            </Grid>
          </Paper>
        </Grid>
      </Grid>
      <Grid item sm={1} md={2} />
    </Grid>
  );
}

export default App;

