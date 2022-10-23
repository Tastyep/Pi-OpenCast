import React, { useState } from "react";
import {
  Box,
  Collapse,
  Grid,
  IconButton,
  Stack,
  Typography,
} from "@mui/material";
import { styled } from "@mui/material/styles";

import PauseIcon from "@mui/icons-material/Pause";
import PlayArrowIcon from "@mui/icons-material/PlayArrow";
import StopIcon from "@mui/icons-material/Stop";
import ClosedCaptionIcon from "@mui/icons-material/ClosedCaption";
import ClosedCaptionDisabledIcon from "@mui/icons-material/ClosedCaptionDisabled";
import AddCircleOutlineIcon from "@mui/icons-material/AddCircleOutline";
import RemoveCircleOutlineIcon from "@mui/icons-material/RemoveCircleOutline";
import FastRewindIcon from "@mui/icons-material/FastRewind";
import FastForwardIcon from "@mui/icons-material/FastForward";
import ArrowLeftIcon from "@mui/icons-material/ArrowLeft";
import ArrowRightIcon from "@mui/icons-material/ArrowRight";
import SkipNextIcon from "@mui/icons-material/SkipNext";
import SkipPreviousIcon from "@mui/icons-material/SkipPrevious";
import ExpandMoreIcon from "@mui/icons-material/ExpandMore";
import VolumeUpIcon from "@mui/icons-material/VolumeUp";

import { Link } from "react-router-dom";

import MediaQuery from "react-responsive";
import { SIZES } from "constants.js";

import { VolumeControl } from "components/volume_control";

import { durationToHMS } from "services/duration";
import playerAPI from "services/api/player";
import snackBarHandler from "services/api/error";

import "./player_control.css";
import { useAppStore } from "providers/app_context";
import { observer } from "mobx-react-lite";
import { useTheme } from "@emotion/react";

const StyledLink = styled(Link)({
  color: "inherit",
  textDecoration: "none",
});

const BarContainer = styled(Stack)(({ theme }) => ({
  backgroundColor: theme.palette.primary.main,
  alignItems: "center",
  flexDirection: "row",
  justifyContent: "space-between",
  height: "56px",
}));

const updatePlayer = (store, update, ...args) => {
  update(...args).catch(snackBarHandler(store));
};

const MediaData = observer((props) => {
  const { video, sx, smallLayout = false } = props;

  const store = useAppStore();
  const artist = store.artists[video.artist_id];
  const album = store.albums[video.album_id];

  if (!smallLayout) {
    const artistBloc = artist ? (
      <StyledLink to={`/artists/${artist.id}`}>{artist.name}</StyledLink>
    ) : (
      "Artist"
    );

    const albumBloc = album ? (
      <StyledLink to={`/albums/${album.id}`}>{album.name}</StyledLink>
    ) : (
      "Album"
    );

    const HMSDuration = durationToHMS(video.duration * 1000);

    return (
      <Stack sx={sx}>
        <Typography color="primary.contrastText" noWrap>
          {" "}
          {video.title}
        </Typography>
        <Grid
          container
          direction="row"
          sx={{ flexWrap: "nowrap", minWidth: "0px" }}
        >
          <Grid item zeroMinWidth>
            <Typography color="primary.contrastText" noWrap>
              {artistBloc}
            </Typography>
          </Grid>
          <Grid item zeroMinWidth>
            <Stack direction="row">
              <Typography
                color="primary.contrastText"
                sx={{ padding: "0px 4px" }}
              >
                •
              </Typography>
              <Typography color="primary.contrastText" noWrap>
                {albumBloc}
              </Typography>
            </Stack>
          </Grid>
          <Grid item>
            <Stack direction="row">
              <Typography
                color="primary.contrastText"
                sx={{ padding: "0px 4px" }}
              >
                •
              </Typography>
              <Typography color="primary.contrastText" noWrap>
                {HMSDuration}
              </Typography>
            </Stack>
          </Grid>
        </Grid>
      </Stack>
    );
  }

  return (
    <Box sx={sx}>
      <Typography color="primary.contrastText">{video.title}</Typography>
    </Box>
  );
});

const PausePlayIcon = observer((props) => {
  const store = useAppStore();
  const isPlayerPlaying = store.player.isPlaying;
  const { sx } = props;

  return (
    <IconButton
      size="small"
      color="secondary"
      sx={sx}
      onClick={() => updatePlayer(store, playerAPI.pauseMedia)}
    >
      {isPlayerPlaying ? (
        <PauseIcon sx={{ fontSize: 30 }} />
      ) : (
        <PlayArrowIcon sx={{ fontSize: 30 }} />
      )}
    </IconButton>
  );
});

const ActiveMediaData = observer(({ variant }) => {
  const store = useAppStore();
  const activeVideo = store.videos[store.player.videoId];

  if (!activeVideo) {
    return null;
  }

  if (variant === "big") {
    return (
      <>
        {activeVideo.thumbnail ? (
          <img
            src={activeVideo.thumbnail}
            alt={activeVideo.title}
            style={{ height: "100%" }}
          />
        ) : (
          <div
            style={{
              height: "100%",
              aspectRatio: "16/9",
              background:
                "linear-gradient(to bottom right, #444647 0%, #626466 50%, #444647 100%)",
            }}
          >
            <Stack
              justifyContent="center"
              alignItems="center"
              style={{
                height: "100%",
                width: "100%",
                background: "rgba(0,0,0,0.3)",
              }}
            >
              <VolumeUpIcon sx={{ color: "rgba(0,0,0,0.5)" }} />
            </Stack>
          </div>
        )}
        <MediaData
          video={activeVideo}
          sx={{ marginLeft: "8px", minWidth: "0px", overflow: "hidden" }}
        />
      </>
    );
  }
  return (
    <>
      {activeVideo.thumbnail ? (
        <img
          src={activeVideo.thumbnail}
          alt={activeVideo.title}
          style={{
            height: "100%",
            aspectRatio: "1/1",
            objectFit: "cover",
          }}
        />
      ) : (
        <div
          style={{
            height: "100%",
            aspectRatio: "1/1",
            background:
              "linear-gradient(to bottom right, #C6FFDD 0%, #FBD786 50%, #F7797D 100%)",
          }}
        >
          <Stack
            justifyContent="center"
            alignItems="center"
            style={{
              height: "100%",
              width: "100%",
              background: "rgba(0,0,0,0.25)",
            }}
          >
            <VolumeUpIcon sx={{ color: "rgba(255,255,255,1)" }} />
          </Stack>
        </div>
      )}
      <MediaData
        smallLayout
        video={activeVideo}
        sx={{ marginLeft: "8px", minWidth: "0px", overflow: "hidden" }}
      />
    </>
  );
});

const SubtitleControl = observer(() => {
  const store = useAppStore();

  return (
    <>
      <IconButton
        size="small"
        color="secondary"
        onClick={() =>
          updatePlayer(
            store,
            playerAPI.seekSubtitle,
            store.player.subDelay - 100
          )
        }
      >
        <RemoveCircleOutlineIcon />
      </IconButton>
      <IconButton
        size="small"
        color="secondary"
        onClick={() => updatePlayer(store, playerAPI.toggleSubtitle)}
      >
        {store.player.subState ? (
          <ClosedCaptionIcon />
        ) : (
          <ClosedCaptionDisabledIcon />
        )}
      </IconButton>
      <IconButton
        size="small"
        color="secondary"
        onClick={() =>
          updatePlayer(
            store,
            playerAPI.seekSubtitle,
            store.player.subDelay + 100
          )
        }
      >
        <AddCircleOutlineIcon />
      </IconButton>
    </>
  );
});

const ControlBar = observer((props) => {
  const store = useAppStore();

  const { openTrackInfo } = props;
  const [expanded, setExpanded] = useState(false);
  const activeVideo = store.videos[store.player.videoId];

  const playNext = () => {
    if (!activeVideo) {
      store.enqueueSnackbar({
        message: "no active media",
        options: {
          variant: "error",
        },
      });
      return;
    }

    const playlist = store.playerPlaylist;
    const idx = playlist.ids.indexOf(activeVideo.id);

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
    if (!activeVideo) {
      store.enqueueSnackbar({
        message: "no active media",
        options: {
          variant: "error",
        },
      });
      return;
    }

    const playlist = store.playerPlaylist;
    const idx = playlist.ids.indexOf(activeVideo.id);

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

  const seekStep = {
    small: 5000,
    big: 30000,
  };

  // Highlight subtitle button when on
  return (
    <MediaQuery minWidth={SIZES.large.min}>
      {(matches) =>
        matches ? (
          <BarContainer sx={{ padding: "0px 16px" }}>
            <Stack direction="row">
              <IconButton size="small" color="secondary" onClick={playPrev}>
                <SkipPreviousIcon />
              </IconButton>
              <PausePlayIcon />
              <IconButton
                size="small"
                color="secondary"
                disableFocusRipple
                disableRipple
                onClick={() => updatePlayer(store, playerAPI.stopMedia)}
              >
                <StopIcon />
              </IconButton>
              <IconButton size="small" color="secondary" onClick={playNext}>
                <SkipNextIcon />
              </IconButton>

              <IconButton
                size="small"
                color="secondary"
                onClick={() =>
                  updatePlayer(
                    store,
                    playerAPI.seekMedia,
                    Math.round(activeVideo.playTime - seekStep.big)
                  )
                }
                sx={{ marginLeft: "16px" }}
              >
                <FastRewindIcon />
              </IconButton>
              <IconButton
                size="small"
                color="secondary"
                onClick={() =>
                  updatePlayer(
                    store,
                    playerAPI.seekMedia,
                    Math.round(activeVideo.playTime - seekStep.small)
                  )
                }
              >
                <ArrowLeftIcon />
              </IconButton>
              <IconButton
                size="small"
                color="secondary"
                onClick={() =>
                  updatePlayer(
                    store,
                    playerAPI.seekMedia,
                    Math.round(activeVideo.playTime + seekStep.small)
                  )
                }
              >
                <ArrowRightIcon />
              </IconButton>
              <IconButton
                size="small"
                color="secondary"
                onClick={() =>
                  updatePlayer(
                    store,
                    playerAPI.seekMedia,
                    Math.round(activeVideo.playTime + seekStep.big)
                  )
                }
              >
                <FastForwardIcon />
              </IconButton>
            </Stack>

            <Stack
              direction="row"
              alignItems="center"
              sx={{
                height: "100%",
                minWidth: "0px",
                margin: "0px 16px",
                overflow: "hidden",
              }}
            >
              <ActiveMediaData variant="big" />
            </Stack>

            <Stack direction="row">
              <VolumeControl
                iconColor="secondary"
                sliderColor="secondary"
                sx={{ minWidth: "320px" }}
              />
              <SubtitleControl />
            </Stack>
          </BarContainer>
        ) : (
          <BarContainer>
            <Stack
              direction="row"
              alignItems="center"
              style={{ height: "100%", minWidth: "0px" }}
            >
              <ActiveMediaData variant="small" />
            </Stack>
            <PausePlayIcon sx={{ marginLeft: "auto" }} />
            <IconButton
              size="medium"
              color="secondary"
              onClick={() => openTrackInfo()}
            >
              <ExpandMoreIcon sx={{ fontSize: 30 }} />
            </IconButton>
          </BarContainer>
        )
      }
    </MediaQuery>
  );
});

export default ControlBar;
