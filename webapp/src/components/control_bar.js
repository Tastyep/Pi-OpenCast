import React, { useState } from "react";
import { Collapse, Grid, IconButton, Stack, Typography } from "@mui/material";
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
import ExpandLessIcon from "@mui/icons-material/ExpandLess";
import ExpandMoreIcon from "@mui/icons-material/ExpandMore";
import VolumeUpIcon from "@mui/icons-material/VolumeUp";

import { Link } from "react-router-dom";

import MediaQuery from "react-responsive";
import { SIZES } from "constants.js";

import VolumeControl from "components/volume_control";

import { durationToHMS } from "services/duration";
import playerAPI from "services/api/player";
import snackBarHandler from "services/api/error";

import "./player_control.css";
import { useAppStore } from "./app_context";
import { observer } from "mobx-react-lite";

const StyledLink = styled(Link)({
  color: "inherit",
  textDecoration: "none",
});

const BarContainer = styled(Stack)({
  backgroundColor: "#F2F2F2",
  alignItems: "center",
  flexDirection: "row",
  justifyContent: "space-between",
  height: "56px",
});

const renderMediaSecondaryData = (artist, album, duration) => {
  const artistBloc = artist ? (
    <StyledLink to={`/library/artists/${artist.id}`}>{artist.name}</StyledLink>
  ) : (
    "Artist"
  );

  const albumBloc = album ? (
    <StyledLink to={`/library/albums/${album.id}`}>{album.name}</StyledLink>
  ) : (
    "Album"
  );

  const HMSDuration = durationToHMS(duration);

  return (
    <Grid
      container
      direction="row"
      sx={{ flexWrap: "nowrap", color: "#505050", minWidth: "0px" }}
    >
      <Grid item zeroMinWidth>
        <Typography noWrap>{artistBloc}</Typography>
      </Grid>
      <Grid item zeroMinWidth>
        <Stack direction="row">
          <Typography sx={{ padding: "0px 4px" }}>•</Typography>
          <Typography noWrap>{albumBloc}</Typography>
        </Stack>
      </Grid>
      <Grid item>
        <Stack direction="row">
          <Typography sx={{ padding: "0px 4px" }}>•</Typography>
          <Typography noWrap>{HMSDuration}</Typography>
        </Stack>
      </Grid>
    </Grid>
  );
};

const updatePlayer = (store, update, ...args) => {
  update(...args).catch(snackBarHandler(store));
};

const PausePlayIcon = observer(() => {
  const store = useAppStore();
  const isPlayerPlaying = store.player.isPlaying;

  return (
    <IconButton
      size="small"
      onClick={() => updatePlayer(store, playerAPI.pauseMedia)}
    >
      {isPlayerPlaying ? (
        <PauseIcon fontSize="large" />
      ) : (
        <PlayArrowIcon fontSize="large" />
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

  const activeArtist = store.artists[activeVideo.artist_id];
  const activeAlbum = store.albums[activeVideo.album_id];

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
        <Stack
          sx={{
            marginLeft: "8px",
            minWidth: "0px",
            overflow: "hidden",
          }}
        >
          <Typography noWrap> {activeVideo.title}</Typography>
          {renderMediaSecondaryData(
            activeArtist,
            activeAlbum,
            activeVideo.duration
          )}
        </Stack>
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
      <Stack
        sx={{
          marginLeft: "8px",
          minWidth: "0px",
          overflow: "hidden",
        }}
      >
        <Typography noWrap variant="body2">
          {activeVideo.title}
        </Typography>
      </Stack>
    </>
  );
});

const SubtitleControl = observer(() => {
  const store = useAppStore();

  return (
    <>
      <IconButton
        size="small"
        onClick={() => updatePlayer(store, playerAPI.seekSubtitle, store.player.subDelay - 100)}
      >
        <RemoveCircleOutlineIcon />
      </IconButton>
      <IconButton
        size="small"
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
        onClick={() => updatePlayer(store, playerAPI.seekSubtitle, store.player.subDelay + 100)}
      >
        <AddCircleOutlineIcon />
      </IconButton>
    </>
  );
});

const ControlBar = observer(() => {
  const store = useAppStore();

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
          <BarContainer direction="row">
            <Stack direction="row">
              <IconButton size="small" onClick={playPrev}>
                <SkipPreviousIcon />
              </IconButton>
              <PausePlayIcon />
              <IconButton
                size="small"
                disableFocusRipple
                disableRipple
                onClick={() => updatePlayer(store, playerAPI.stopMedia)}
              >
                <StopIcon />
              </IconButton>
              <IconButton size="small" onClick={playNext}>
                <SkipNextIcon />
              </IconButton>

              <IconButton
                size="small"
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
              <VolumeControl />
              <SubtitleControl />
            </Stack>
          </BarContainer>
        ) : (
          <div style={{ minHeight: "auto" }}>
            <Collapse
              in={expanded}
              timeout="auto"
              unmountOnExit
              sx={{
                minHeight: "auto",
              }}
            >
              <Grid
                container
                sx={{ paddingBottom: "8px", backgroundColor: "#F2F2F2" }}
              >
                <Grid item xs={12} sx={{ paddingLeft: "8px" }}>
                  <VolumeControl />
                </Grid>
                <Grid item xs={6}>
                  <IconButton
                    size="small"
                    onClick={() =>
                      updatePlayer(
                        store,
                        playerAPI.seekMedia,
                        Math.round(activeVideo.playTime - seekStep.big)
                      )
                    }
                  >
                    <FastRewindIcon />
                  </IconButton>
                  <IconButton
                    size="small"
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
                    disableFocusRipple
                    disableRipple
                    onClick={() => updatePlayer(store, playerAPI.stopMedia)}
                  >
                    <StopIcon />
                  </IconButton>
                  <IconButton
                    size="small"
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
                </Grid>
                <Grid item container xs={6} justifyContent="flex-end">
                  <SubtitleControl />
                </Grid>
              </Grid>
            </Collapse>
            <BarContainer direction="row">
              <Stack
                direction="row"
                alignItems="center"
                style={{ height: "100%", minWidth: "0px" }}
              >
                <ActiveMediaData variant="small" />
              </Stack>
              <Stack direction="row">
                <IconButton size="small" onClick={playPrev}>
                  <SkipPreviousIcon />
                </IconButton>
                <PausePlayIcon />
                <IconButton size="small" onClick={playNext}>
                  <SkipNextIcon />
                </IconButton>
                <IconButton
                  size="medium"
                  onClick={() => setExpanded(!expanded)}
                >
                  {expanded ? <ExpandMoreIcon /> : <ExpandLessIcon />}
                </IconButton>
              </Stack>
            </BarContainer>
          </div>
        )
      }
    </MediaQuery>
  );
});

export default ControlBar;
