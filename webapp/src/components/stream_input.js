import React, { useState } from "react";

import { useTheme } from "@mui/material/styles";

import Box from "@mui/material/Box";
import Button from "@mui/material/Button";
import Collapse from "@mui/material/Collapse";
import InputBase from "@mui/material/InputBase";
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
import MenuIcon from "@mui/icons-material/Menu";

import playerAPI from "services/api/player";
import snackBarHandler from "services/api/error";
import { mixColor } from "services/color";

import { useAppStore } from "providers/app_context";

const StreamInput = (props) => {
  const { sx } = props;

  const store = useAppStore();

  const [url, setUrl] = useState("");
  const [streamOpt, setStreamOpt] = useState(true);
  const [audioOnlyOpt, setAudioOnlyOpt] = useState(false);
  const [subtitleDlOpt, setSubtitleDlOpt] = useState(false);
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
        .streamMedia(url, { dl_opts: { download_video: audioOnlyOpt } })
        .catch(snackBarHandler(store));
    } else {
      playerAPI
        .queueMedia(url, { dl_opts: { download_video: audioOnlyOpt } })
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
    console.log("value: ", value);
    setAudioOnlyOpt(value === "audio");
    setSubtitleDlOpt(value !== "audio");
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
        color="secondary"
        onClick={() => setExpanded(!expanded)}
      >
        <MoreVertIcon />
      </IconButton>
    </InputAdornment>
  );

  const theme = useTheme();
  const inputBackground = mixColor(theme.palette.primary.main, "#FFFFFF", 0.18);

  return (
    <Box sx={sx}>
      <form onSubmit={handleSubmit} noValidate autoComplete="off">
        <Stack direction="row">
          <IconButton color="inherit" onClick={() => setExpanded(!expanded)}>
            <MenuIcon />
          </IconButton>
          <InputBase
            fullWidth
            placeholder="Media's URL"
            value={url}
            sx={{
              color: theme.palette.primary.contrastText,
              backgroundColor: inputBackground,
              borderRadius: "16px",
              margin: "0px 8px",
              padding: "0px 16px",
            }}
            onChange={(e) => setUrl(e.target.value)}
            onKeyPress={updateBlur}
          />
          <IconButton color="inherit" onClick={handleSubmit}>
            <SendIcon sx={{ fontSize: "20px" }} />
          </IconButton>
        </Stack>
      </form>
      <Box sx={{ display: "flex" }}>
        <Collapse
          in={expanded}
          timeout="auto"
          unmountOnExit
          sx={{ backgroundColor: theme.palette.primary.main }}
        >
          <List>
            <ListItem
              alignItems="center"
              sx={{ paddingLeft: "0px", paddingRight: "0px" }}
            >
              <ToggleButtonGroup
                color="secondary"
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
              <Typography
                noWrap
                color="primary.contrastText"
                sx={{ marginLeft: "16px" }}
              >
                {streamOpt ? "Play next" : "Queue last"}
              </Typography>
            </ListItem>
            <ListItem
              alignItems="center"
              sx={{ paddingLeft: "0px", paddingRight: "0px" }}
            >
              <ToggleButtonGroup
                color="secondary"
                value={audioOnlyOpt ? "audio" : "video"}
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
              <Typography
                noWrap
                color="primary.contrastText"
                sx={{ marginLeft: "16px" }}
              >
                {audioOnlyOpt ? "Audio only" : "Video"}
              </Typography>
            </ListItem>
          </List>
        </Collapse>
      </Box>
    </Box>
  );
};

export default StreamInput;
