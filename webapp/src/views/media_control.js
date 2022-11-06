import Typography from "@mui/material/Typography";
import Card from "@mui/material/Card";
import CardContent from "@mui/material/CardContent";
import CardMedia from "@mui/material/CardMedia";
import Stack from "@mui/material/Stack";
import IconButton from "@mui/material/IconButton";
import Grid from "@mui/material/Grid";

import MusicVideoIcon from "@mui/icons-material/MusicVideo";
import StopIcon from "@mui/icons-material/Stop";
import SkipNextIcon from "@mui/icons-material/SkipNext";
import SkipPreviousIcon from "@mui/icons-material/SkipPrevious";
import PauseCircleFilledIcon from "@mui/icons-material/PauseCircleFilled";
import PlayCircleFilledIcon from "@mui/icons-material/PlayCircleFilled";
import ClosedCaptionIcon from "@mui/icons-material/ClosedCaption";
import ClosedCaptionDisabledIcon from "@mui/icons-material/ClosedCaptionDisabled";
import RemoveCircleOutlineIcon from "@mui/icons-material/RemoveCircleOutline";
import FastRewindIcon from "@mui/icons-material/FastRewind";
import FastForwardIcon from "@mui/icons-material/FastForward";
import ArrowLeftIcon from "@mui/icons-material/ArrowLeft";
import ArrowRightIcon from "@mui/icons-material/ArrowRight";
import Replay5Icon from "@mui/icons-material/Replay5";
import Forward5Icon from "@mui/icons-material/Forward5";

import { observer } from "mobx-react-lite";

import PlayerProgress from "components/player_progress";
import { VolumeControl } from "components/volume_control";
import { PausePlayButton, SubtitleButtons } from "components/player_buttons";

import playerAPI from "services/api/player";
import { durationToHMS, countHMSParts } from "services/duration";
import snackBarHandler from "services/api/error";

import { useAppStore } from "providers/app_context";

const updatePlayer = (store, update, ...args) => {
  update(...args).catch(snackBarHandler(store));
};
const MediaControl = observer((props) => {
  const { iconColor, buttonSize = "medium", iconSize = "large" } = props;

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

  return (
    <Card>
      {video.thumbnail ? (
        <CardMedia component="img" image={video.thumbnail} alt={video.title} />
      ) : null}

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
          flexDirection: "column",
          flex: 1,
        }}
      >
        <Grid container direction="row">
          <Grid item xs={4} sx={{ maxWidth: "296px" }}>
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

          <Grid
            container
            item
            alignContent="center"
            justifyContent="center"
            xs={4}
          >
            <Typography noWrap variant="h4" sx={{ marginRight: "24px" }}>
              {artist && `artist.name - `} {video.title}
            </Typography>
          </Grid>
          <Grid container item justifyContent="flex-end" xs={4}>
            <SubtitleButtons iconColor={iconColor} iconSize={iconSize} />
          </Grid>
        </Grid>

        <VolumeControl
          iconColor={iconColor}
          height={3}
          sx={{ marginTop: "24px" }}
        />
      </CardContent>
    </Card>
  );
});

export default MediaControl;
