import { useState } from "react";

import Typography from "@mui/material/Typography";
import Card from "@mui/material/Card";
import CardContent from "@mui/material/CardContent";
import CardMedia from "@mui/material/CardMedia";
import Stack from "@mui/material/Stack";
import IconButton from "@mui/material/IconButton";
import Grid from "@mui/material/Grid";
import Box from "@mui/material/Box";
import Popper from "@mui/material/Popper";
import Divider from "@mui/material/Divider";

import SkipNextIcon from "@mui/icons-material/SkipNext";
import SkipPreviousIcon from "@mui/icons-material/SkipPrevious";
import Replay5Icon from "@mui/icons-material/Replay5";
import Forward5Icon from "@mui/icons-material/Forward5";
import SettingsIcon from "@mui/icons-material/Settings";

import { useTheme } from "@emotion/react";

import { observer } from "mobx-react-lite";

import PlayerProgress from "components/player_progress";
import { VolumeControl } from "components/volume_control";
import { PausePlayButton, SubtitleButtons } from "components/player_buttons";

import playerAPI from "services/api/player";
import { durationToHMS, countHMSParts } from "services/duration";
import snackBarHandler from "services/api/error";

import { useAppStore } from "providers/app_context";
import { useRef } from "react";

const updatePlayer = (store, update, ...args) => {
  update(...args).catch(snackBarHandler(store));
};

const AdvancedPlayerControl = observer((props) => {
  const { anchorEl, placement, iconColor, iconSize } = props;
  const open = Boolean(anchorEl);
  const id = open ? "advanced-player-control" : undefined;

  const theme = useTheme();
  const menuWidth = 256;

  if (!open) {
    return null;
  }

  console.log(anchorEl.clientHeight);
  return (
    <Popper
      id={id}
      open={open}
      anchorEl={anchorEl}
      placement={placement}
      modifiers={[
        {
          name: "offset",
          options: {
            offset: [0, -anchorEl.clientHeight],
          },
        },
      ]}
    >
      <Stack
        direction="row"
        sx={{
          width: menuWidth,
          height: anchorEl.clientHeight,
          backgroundColor: theme.palette.background.default,
          boxSizing: "border-box",
        }}
      >
        <Divider orientation="vertical" />
        <Stack
          direction="column"
          sx={{
            flex: 1,
            padding: "24px 16px 24px 16px",
          }}
        >
          <Typography variant="h5">Advanced control</Typography>
          <Stack direction="row">
            <SubtitleButtons iconColor={iconColor} iconSize={iconSize} />
          </Stack>
        </Stack>
      </Stack>
    </Popper>
  );
});

const MediaControl = observer((props) => {
  const { iconColor, buttonSize = "medium", iconSize = "large" } = props;
  const [advancedControlAnchor, setAdvancedControlAnchor] = useState(null);
  const mediaImageRef = useRef();

  const store = useAppStore();
  const video = store.videos[store.player.videoId];

  if (!video) {
    return null;
  }

  const artist = store.artists[video.artistId];
  const seekStep = {
    small: 5000,
    big: 30000,
  };

  const playNext = () => {
    if (!video) {
      store.enqueueSnackbar({
        message: "no active media",
        options: {
          variant: "error",
        },
      });
      return;
    }

    const playlist = store.playerPlaylist;
    const idx = playlist.ids.indexOf(video.id);

    if (idx + 1 === playlist.ids.length) {
      store.enqueueSnackbar({
        message: "no more media available",
        options: {
          variant: "error",
        },
      });
      return;
    }

    playerAPI.playMedia(playlist.ids[idx + 1]).catch(snackBarHandler(store));
  };

  const playPrev = () => {
    if (!video) {
      store.enqueueSnackbar({
        message: "no active media",
        options: {
          variant: "error",
        },
      });
      return;
    }

    const playlist = store.playerPlaylist;
    const idx = playlist.ids.indexOf(video.id);

    if (idx - 1 < 0) {
      store.enqueueSnackbar({
        message: "no more media available",
        options: {
          variant: "error",
        },
      });
      return;
    }

    playerAPI.playMedia(playlist.ids[idx - 1]).catch(snackBarHandler(store));
  };

  const toggleAdvancedControls = () => {
    if (advancedControlAnchor) {
      setAdvancedControlAnchor(null);
    } else {
      setAdvancedControlAnchor(mediaImageRef.current);
    }
  };

  return (
    <Card>
      <Box ref={mediaImageRef}>
        {video.thumbnail ? (
          <CardMedia
            component="img"
            image={video.thumbnail}
            alt={video.title}
          />
        ) : null}
        <AdvancedPlayerControl
          anchorEl={advancedControlAnchor}
          placement="bottom-end"
          iconSize={iconSize}
          iconColor={iconColor}
        />
      </Box>

      <Stack direction="column" alignItems="center" sx={{ width: "100%" }}>
        <PlayerProgress height={7} />
        <Stack
          direction="row"
          justifyContent="space-between"
          style={{ width: "98%", marginTop: "8px" }}
        >
          <Typography variant="body2">
            {durationToHMS(
              video.playTime,
              countHMSParts(video.duration * 1000)
            )}
          </Typography>
          <Typography variant="body2">
            {durationToHMS(video.duration * 1000)}
          </Typography>
        </Stack>
      </Stack>

      <CardContent
        sx={{
          display: "flex",
          flex: 1,
          flexDirection: "column",
        }}
      >
        <Stack alignItems="center" sx={{ marginBottom: "16px" }}>
          <Typography noWrap variant="h4">
            {artist && `artist.name - `} {video.title}
          </Typography>
        </Stack>

        <Grid container direction="row">
          <Grid container item xs={11}>
            <IconButton size={buttonSize} color={iconColor} onClick={playPrev}>
              <SkipPreviousIcon fontSize={iconSize} />
            </IconButton>

            <PausePlayButton iconColor={iconColor} iconSize={iconSize} />

            {/* <IconButton */}
            {/*   size={buttonSize} */}
            {/*   color={iconColor} */}
            {/*   disableFocusRipple */}
            {/*   disableRipple */}
            {/*   onClick={() => updatePlayer(store, playerAPI.stopMedia)} */}
            {/* > */}
            {/*   <StopIcon /> */}
            {/* </IconButton> */}
            <IconButton size={buttonSize} color={iconColor} onClick={playNext}>
              <SkipNextIcon fontSize={iconSize} />
            </IconButton>

            <IconButton
              size={buttonSize}
              color={iconColor}
              onClick={() =>
                updatePlayer(
                  store,
                  playerAPI.seekMedia,
                  Math.round(video.playTime - seekStep.small)
                )
              }
            >
              <Replay5Icon fontSize={iconSize} />
            </IconButton>

            <IconButton
              size={buttonSize}
              color={iconColor}
              onClick={() =>
                updatePlayer(
                  store,
                  playerAPI.seekMedia,
                  Math.round(video.playTime + seekStep.small)
                )
              }
            >
              <Forward5Icon fontSize={iconSize} />
            </IconButton>
          </Grid>

          <Grid container item justifyContent="flex-end" xs={1}>
            <IconButton
              size={buttonSize}
              color={iconColor}
              onClick={toggleAdvancedControls}
            >
              <SettingsIcon fontSize={iconSize} />
            </IconButton>
          </Grid>
        </Grid>

        <Stack sx={{ margin: "0px 6px 0px 6px" }}>
          <VolumeControl iconSize="medium" iconColor={iconColor} height={3} />
        </Stack>
      </CardContent>
    </Card>
  );
});

export default MediaControl;
