import React, { useState } from "react";

import Box from "@mui/material/Box";
import Button from "@mui/material/Button";
import Collapse from "@mui/material/Collapse";
import Grid from "@mui/material/Grid";
import Paper from "@mui/material/Paper";
import Stack from "@mui/material/Stack";
import TextField from "@mui/material/TextField";
import ToggleButton from "@mui/material/ToggleButton";
import ToggleButtonGroup from "@mui/material/ToggleButtonGroup";
import Typography from "@mui/material/Typography";

import PlaylistPlayIcon from "@mui/icons-material/PlaylistPlay";
import PlaylistAddIcon from "@mui/icons-material/PlaylistAdd";
import SendIcon from "@mui/icons-material/Send";
import MoreVertIcon from "@mui/icons-material/MoreVert";

import playerAPI from "services/api/player";
import snackBarHandler from "services/api/error";

import { useAppStore } from "components/app_context";

const StreamInput = () => {
  const store = useAppStore();

  const [url, setUrl] = useState("");
  const [action, setAction] = useState(() => playerAPI.streamMedia);
  const [expanded, setExpanded] = useState(false);

  const handleSubmit = (event) => {
    if (event) {
      event.preventDefault();
    }
    if (url === "") {
      return;
    }
    action(url).catch(snackBarHandler(store));
    setUrl("");
  };

  const updateAction = (_, newAction) => {
    if (!newAction) {
      return;
    }
    setAction(
      newAction === "stream"
        ? () => playerAPI.streamMedia
        : () => playerAPI.queueMedia
    );
  };

  const updateBlur = (evt) => {
    if (evt.key === "Enter") {
      evt.target.blur();
    }
  };

  return (
    <Box>
      <form onSubmit={handleSubmit} noValidate autoComplete="off">
        <Stack direction="row">
          <TextField
            fullWidth
            label="Media's URL"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            onKeyPress={updateBlur}
          />
          <Button
            size="medium"
            variant="outlined"
            sx={{
              marginLeft: "16px",
              color: "#333333",
              borderColor: "#8F8F8F",
            }}
            onClick={handleSubmit}
          >
            <SendIcon />
          </Button>
          <Button
            size="small"
            sx={{ color: "#333333" }}
            onClick={() => setExpanded(!expanded)}
          >
            <MoreVertIcon />
          </Button>
        </Stack>
      </form>
      <Box sx={{ display: "flex" }}>
        <Collapse
          in={expanded}
          timeout="auto"
          unmountOnExit
          sx={{
            marginLeft: "auto",
          }}
        >
          <Paper
            sx={{
              maxWidth: "100%",
              marginTop: "8px",
              padding: "16px",
            }}
          >
            <Typography variant="h6" sx={{ marginBottom: "16px" }}>
              Options
            </Typography>
            <Grid container alignItems="center" flexWrap="nowrap">
              <Grid item xs={8} sx={{ marginRight: "16px" }}>
                <ToggleButtonGroup
                  value={action === playerAPI.streamMedia ? "stream" : "queue"}
                  exclusive
                  onChange={updateAction}
                  aria-label="text alignment"
                >
                  <ToggleButton value="stream" aria-label="stream">
                    <PlaylistPlayIcon />
                  </ToggleButton>
                  <ToggleButton value="queue" aria-label="queue">
                    <PlaylistAddIcon />
                  </ToggleButton>
                </ToggleButtonGroup>
              </Grid>
              <Grid item xs>
                <Typography noWrap sx={{ minWidth: "80px" }}>
                  {action === playerAPI.streamMedia
                    ? "Play next"
                    : "Queue last"}
                </Typography>
              </Grid>
            </Grid>
          </Paper>
        </Collapse>
      </Box>
    </Box>
  );
};

export default StreamInput;
