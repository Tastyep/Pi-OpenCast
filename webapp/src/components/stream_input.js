import React, { useState } from "react";

import Box from "@mui/material/Box";
import Button from "@mui/material/Button";
import Collapse from "@mui/material/Collapse";
import IconButton from "@mui/material/IconButton";
import Stack from "@mui/material/Stack";
import TextField from "@mui/material/TextField";
import ToggleButton from "@mui/material/ToggleButton";
import ToggleButtonGroup from "@mui/material/ToggleButtonGroup";
import Typography from "@mui/material/Typography";
import List from "@mui/material/List";
import ListItem from "@mui/material/ListItem";
import InputAdornment from "@mui/material/InputAdornment";

import PlaylistPlayIcon from "@mui/icons-material/PlaylistPlay";
import PlaylistAddIcon from "@mui/icons-material/PlaylistAdd";
import SendIcon from "@mui/icons-material/Send";
import MoreVertIcon from "@mui/icons-material/MoreVert";
import MusicVideoIcon from "@mui/icons-material/MusicVideo";
import MusicNoteIcon from "@mui/icons-material/MusicNote";

import playerAPI from "services/api/player";
import snackBarHandler from "services/api/error";

import { useAppStore } from "providers/app_context";

const StreamInput = () => {
  const store = useAppStore();

  const [url, setUrl] = useState("");
  const [streamOpt, setStreamOpt] = useState(true);
  const [videoOpt, setVideoOpt] = useState(true);
  const [expanded, setExpanded] = useState(false);

  const handleSubmit = (event) => {
    if (event) {
      event.preventDefault();
    }
    if (url === "") {
      return;
    }
    if (streamOpt) {
      playerAPI
        .streamMedia(url, { dl_opts: { download_video: videoOpt } })
        .catch(snackBarHandler(store));
    } else {
      playerAPI
        .queueMedia(url, { dl_opts: { download_video: videoOpt } })
        .catch(snackBarHandler(store));
    }
    setUrl("");
    setExpanded(false);
  };

  const updateAction = (_, value) => {
    if (!value) {
      return;
    }
    setStreamOpt(value === "stream");
  };

  const updateDownloadedChannels = (_, value) => {
    if (!value) {
      return;
    }
    setVideoOpt(value === "video");
  };

  const updateBlur = (evt) => {
    if (evt.key === "Enter") {
      evt.target.blur();
    }
  };

  const menuOptions = (
    <InputAdornment position="end">
      <IconButton
        size="small"
        sx={{
          color: "#333333",
        }}
        onClick={() => setExpanded(!expanded)}
      >
        <MoreVertIcon />
      </IconButton>
    </InputAdornment>
  );

  return (
    <Box>
      <form onSubmit={handleSubmit} noValidate autoComplete="off">
        <Stack direction="row">
          <TextField
            fullWidth
            label="Media's URL"
            value={url}
            InputProps={{
              endAdornment: menuOptions,
            }}
            onChange={(e) => setUrl(e.target.value)}
            onKeyPress={updateBlur}
          />
          <Button
            size="small"
            variant="outlined"
            sx={{
              color: "#333333",
              borderColor: "#8F8F8F",
              marginLeft: "16px",
            }}
            onClick={handleSubmit}
          >
            <SendIcon sx={{ fontSize: "20px" }} />
          </Button>
        </Stack>
      </form>
      <Box sx={{ display: "flex" }}>
        <Collapse in={expanded} timeout="auto" unmountOnExit sx={{}}>
          <List>
            <ListItem
              alignItems="center"
              sx={{ paddingLeft: "0px", paddingRight: "0px" }}
            >
              <ToggleButtonGroup
                value={streamOpt ? "stream" : "queue"}
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
              <Typography noWrap sx={{ marginLeft: "16px" }}>
                {streamOpt ? "Play next" : "Queue last"}
              </Typography>
            </ListItem>
            <ListItem
              alignItems="center"
              sx={{ paddingLeft: "0px", paddingRight: "0px" }}
            >
              <ToggleButtonGroup
                value={videoOpt ? "video" : "audio"}
                exclusive
                onChange={updateDownloadedChannels}
                aria-label="text alignment"
              >
                <ToggleButton value="video" aria-label="video">
                  <MusicVideoIcon />
                </ToggleButton>
                <ToggleButton value="audio" aria-label="audio">
                  <MusicNoteIcon />
                </ToggleButton>
              </ToggleButtonGroup>
              <Typography noWrap sx={{ marginLeft: "16px" }}>
                {videoOpt ? "Video" : "Audio only"}
              </Typography>
            </ListItem>
          </List>
        </Collapse>
      </Box>
    </Box>
  );
};

export default StreamInput;
