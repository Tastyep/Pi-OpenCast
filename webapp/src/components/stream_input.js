import React, { useState } from 'react';
import {
  Box,
  Stack,
  IconButton,
  InputBase,
  Popover,
  Typography,
  ToggleButtonGroup,
  ToggleButton,
  Switch,
  FormControlLabel,
  Divider,
  RadioGroup,
  Radio,
  Button,
} from '@mui/material';

import SendIcon from '@mui/icons-material/Send';
import VideocamIcon from '@mui/icons-material/Videocam';
import AudiotrackIcon from '@mui/icons-material/Audiotrack';

import { useTheme } from '@mui/material/styles';

import { useAppStore } from "providers/app_context";
import { mixColor } from "services/color";
import playerAPI from "services/api/player";
import snackBarHandler from "services/api/error";


const StreamInput = ({ sx }) => {
  const store = useAppStore();
  const theme = useTheme();
  const inputBackground = mixColor(theme.palette.primary.dark, '#FFFFFF', 0.18);

  const [url, setUrl] = useState('');
  const [optionsAnchor, setOptionsAnchor] = useState(null);
  const [expanded, setExpanded] = useState(false);

  const [downloadMode, setDownloadMode] = useState('video'); // 'video' | 'audio'
  const [subtitleDlOpt, setSubtitleDlOpt] = useState(false);
  const [action, setAction] = useState('play'); // 'play' | 'queue'

  const openOptions = (e) => {
    setOptionsAnchor(e.currentTarget);
    setExpanded(true);
  };

  const closeOptions = () => {
    setOptionsAnchor(null);
    setExpanded(false);
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!url) return;

    const dl_opts = {
      download_video: downloadMode === 'video',
      download_subtitles: subtitleDlOpt,
    };

    const apiCall =
      action === 'play'
        ? playerAPI.streamMedia(url, { dl_opts })
        : playerAPI.queueMedia(url, { dl_opts });

    apiCall.catch(snackBarHandler(store));
    closeOptions();
    setUrl('');
  };

  return (
    <Box sx={sx}>
      <form onSubmit={handleSubmit} noValidate autoComplete="off">
        <Stack direction="row" alignItems="center" spacing={1}>
          {/* Options button shows current mode */}
          <IconButton
            color="inherit"
            aria-label="Options"
            onClick={openOptions}
          >
            {downloadMode === 'audio' ? (
              <AudiotrackIcon />
            ) : (
              <VideocamIcon />
            )}
          </IconButton>

          {/* URL input */}
          <InputBase
            fullWidth
            placeholder="Media's URL"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            sx={{
              color: theme.palette.primary.contrastText,
              backgroundColor: inputBackground,
              borderRadius: '16px',
              mx: 1,
              px: 2,
              py: 0.5,
            }}
          />

          {/* Submit */}
          <IconButton color="inherit" type="submit">
            <SendIcon sx={{ fontSize: 20 }} />
          </IconButton>
        </Stack>
      </form>

      {/* Popover for all options */}
      <Popover
        open={expanded}
        anchorEl={optionsAnchor}
        onClose={closeOptions}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'left' }}
      >
        <Box sx={{ width: 260, p: 2 }}>
          {/* Download Settings */}
          <Typography variant="subtitle2" gutterBottom>
            Download Settings
          </Typography>
          <ToggleButtonGroup
            value={downloadMode}
            exclusive
            fullWidth
            size="small"
            onChange={(_, val) => val && setDownloadMode(val)}
            sx={{ mb: 2 }}
            aria-label="Download Mode"
          >
            <ToggleButton value="video" aria-label="Download video">
              <VideocamIcon fontSize="small" sx={{ mr: 0.5 }} /> Video
            </ToggleButton>
            <ToggleButton value="audio" aria-label="Download audio only">
              <AudiotrackIcon fontSize="small" sx={{ mr: 0.5 }} /> Audio
            </ToggleButton>
          </ToggleButtonGroup>

          {/* Subtitle Option */}
          <FormControlLabel
            control={
              <Switch
                checked={subtitleDlOpt}
                onChange={(e) => setSubtitleDlOpt(e.target.checked)}
                size="small"
              />
            }
            label="Download Subtitles"
            sx={{ mb: 2 }}
          />

          {/* Divider */}
          <Divider sx={{ my: 1 }} />

          {/* Playback Settings */}
          <Typography variant="subtitle2" gutterBottom>
            Playback Settings
          </Typography>
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

          {/* Done button */}
          <Box textAlign="right" mt={2}>
            <Button size="small" onClick={closeOptions}>
              Done
            </Button>
          </Box>
        </Box>
      </Popover>
    </Box>
  );
};

export default StreamInput;
