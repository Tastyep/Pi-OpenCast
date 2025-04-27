import React, { useState } from "react";

import { useTheme } from "@mui/material/styles";

import Box from "@mui/material/Box";
import Button from "@mui/material/Button";
import InputBase from "@mui/material/InputBase";
import IconButton from "@mui/material/IconButton";
import Stack from "@mui/material/Stack";
import ToggleButton from "@mui/material/ToggleButton";
import ToggleButtonGroup from "@mui/material/ToggleButtonGroup";
import FormControlLabel from "@mui/material/FormControlLabel";
import RadioGroup from "@mui/material/RadioGroup";

import {
  Popover,
  Radio,
} from '@mui/material';

import SendIcon from "@mui/icons-material/Send";
import MenuIcon from "@mui/icons-material/Menu";

import playerAPI from "services/api/player";
import snackBarHandler from "services/api/error";
import { mixColor } from "services/color";

import { useAppStore } from "providers/app_context";

const StreamInput = (props) => {
  const { sx } = props;

  const store = useAppStore();

  const [url, setUrl] = useState("");
  const [optionsAnchor, setOptionsAnchor] = useState(null);
  const [audioOnlyOpt, setAudioOnlyOpt] = useState(false);
  const [action, setAction] = useState('play');
  const [subtitleDlOpt, setSubtitleDlOpt] = useState(false);
  const [expanded, setExpanded] = useState(false);


  const openOptions = (e) => {
    setOptionsAnchor(e.currentTarget);
    setExpanded(true);
  };

  const closeOptions = (e) => {
    setOptionsAnchor(null);
    setExpanded(false);
  };

  const applyOptions = () => {
    // use mode & action when downloading/submitting
    closeOptions();
  };

  const handleSubmit = (event) => {
    if (event) {
      event.preventDefault();
    }

    if (url === "") {
      return;
    }

    if (action === "play") {
      playerAPI
        .streamMedia(url, {
          dl_opts: {
            download_video: !audioOnlyOpt,
            download_subtitles: subtitleDlOpt,
          },
        })
        .catch(snackBarHandler(store));
    } else {
      playerAPI
        .queueMedia(url, {
          dl_opts: {
            download_video: !audioOnlyOpt,
            download_subtitles: subtitleDlOpt,
          },
        })
        .catch(snackBarHandler(store));
    }

    closeOptions();
    setUrl("");
  };

  const setDownloadedChannels = (value) => {
    if (!value) {
      return;
    }

    setAudioOnlyOpt(value === "audio");
    console.log("audioOnly:", audioOnlyOpt)
    // TODO: add real support for downloading subtitles.
    // Add a button for enabling subtitle downloading.
    // Add another one for downloading subtitles after downloading a video
    // setSubtitleDlOpt(value !== "audio");
  };

  const updateBlur = (evt) => {
    if (evt.key === "Enter") {
      evt.target.blur();
    }
  };

  const theme = useTheme();
  const inputBackground = mixColor(theme.palette.primary.dark, "#FFFFFF", 0.18);

  return (
    <Box sx={sx}>
      <form onSubmit={handleSubmit} noValidate autoComplete="off">
        <Stack direction="row">
          <IconButton color="inherit" onClick={openOptions}>
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
      <Popover
        open={expanded}
        anchorEl={optionsAnchor}
        onClose={closeOptions}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'left' }}
      >
        <Stack spacing={2} p={2} sx={{ width: 240 }}>
          {/* Download Mode */}
          <ToggleButtonGroup
            value={audioOnlyOpt ? "audio" : "video"}
            exclusive
            onChange={(_, val) => val && setDownloadedChannels(val)}
            aria-label="download mode"
          >
            <ToggleButton value="video">Video</ToggleButton>
            <ToggleButton value="audio">Audio</ToggleButton>
          </ToggleButtonGroup>

          {/* Playback Action */}
          <RadioGroup
            value={action}
            onChange={(e) => setAction(e.target.value)}
          >
            <FormControlLabel
              value="play"
              control={<Radio size="small" />}
              label="Play Now"
            />
            <FormControlLabel
              value="queue"
              control={<Radio size="small" />}
              label="Add to Queue"
            />
          </RadioGroup>

          <Button variant="contained" onClick={applyOptions}>
            Apply
          </Button>
        </Stack>
      </Popover>
    </Box>
  );
};

export default StreamInput;
