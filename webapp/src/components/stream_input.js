import React, { Component } from "react";

import { TextField, Button, ButtonGroup, Grid } from "@material-ui/core";
import { makeStyles } from "@material-ui/core/styles";

import player from "services/api/player";

import "./stream_input.css";

function StreamInput() {
  const [url, setUrl] = React.useState("");
  const [action, setAction] = React.useState(undefined);

  const handleSubmit = (event) => {
    event.preventDefault();
    if (url === "") {
      return;
    }
    action(url);
    setUrl("");
    setAction(undefined);
  };

  return (
    <form onSubmit={handleSubmit} noValidate autoComplete="off">
      <Grid container spacing={1}>
        <Grid item xs={9}>
          <TextField
            fullWidth
            id="outlined-basic"
            label="Media's URL"
            variant="standard"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
          />
        </Grid>
        <Grid item xs={1} />
        <Grid item xs={2} className="StreamButtons">
          <ButtonGroup
            orientation="vertical"
            color="primary"
            aria-label="vertical contained primary button group"
            variant="text"
          >
            <Button
              type="submit"
              onClick={() => setAction(() => player.streamMedia)}
            >
              Cast
            </Button>
            <Button
              type="submit"
              onClick={() => setAction(() => player.queueMedia)}
            >
              Queue
            </Button>
          </ButtonGroup>
        </Grid>
      </Grid>
    </form>
  );
}

export default StreamInput;
