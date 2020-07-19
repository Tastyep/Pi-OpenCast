import React, { useState } from "react";

import { TextField, Button, ButtonGroup, Grid } from "@material-ui/core";

import player from "services/api/player";

import "./stream_input.css";

function StreamInput() {
  const [url, setUrl] = React.useState("");
  const [action, setAction] = React.useState(() => player.streamMedia);
  const [castVariant, setCastVariant] = React.useState("contained");
  const [queueVariant, setQueueVariant] = React.useState("outlined");

  const handleSubmit = (event) => {
    if (event) {
      event.preventDefault();
    }
    if (url === "") {
      return;
    }
    action(url);
    setUrl("");
  };

  const handleActionChange = (cast) => {
    if (cast === true) {
      setCastVariant("contained");
      setQueueVariant("outlined");
      setAction(() => player.streamMedia);
    } else {
      setCastVariant("outlined");
      setQueueVariant("contained");
      setAction(() => player.queueMedia);
    }
    handleSubmit(undefined);
  };

  return (
    <form onSubmit={(e) => handleSubmit(e)} noValidate autoComplete="off">
      <Grid container spacing={1}>
        <Grid item xs={6} sm={7} md={8}>
          <TextField
            fullWidth
            id="outlined-basic"
            label="Media's URL"
            variant="standard"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
          />
        </Grid>
        <Grid item xs={6} sm={5} md={4} className="StreamButtons">
          <ButtonGroup
            size="medium"
            color="primary"
            aria-label="vertical contained primary button group"
          >
            <Button
              variant={castVariant}
              onClick={() => handleActionChange(true)}
            >
              Cast
            </Button>
            <Button
              variant={queueVariant}
              onClick={() => handleActionChange(false)}
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
