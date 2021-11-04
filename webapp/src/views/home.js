import React, { useCallback } from "react";

import { styled } from "@mui/material/styles";

import {
  Container,
  Grid,
  List,
  Divider,
  ListItem,
  ListItemText,
  ListItemAvatar,
  Avatar,
  ListSubheader,
  LinearProgress,
  Stack,
} from "@mui/material";
import Typography from "@mui/material/Typography";
import IconButton from "@mui/material/IconButton";
import PlayArrowIcon from "@mui/icons-material/PlayArrow";
import VolumeUpIcon from "@mui/icons-material/VolumeUp";
import ClearAllIcon from "@mui/icons-material/ClearAll";

import { DragDropContext, Draggable, Droppable } from "react-beautiful-dnd";

import MediaQuery from "react-responsive";
import { SIZES } from "constants.js";

import { observer } from "mobx-react-lite";

import noPreview from "images/no-preview.png";
import playerAPI from "services/api/player";
import playlistAPI from "services/api/playlist";
import snackBarHandler from "services/api/error";
import { durationToHMS } from "services/duration";

import { useAppStore } from "components/app_context";
import StreamInput from "components/stream_input";

const PageContainer = styled("div")({
  display: "flex",
  flexWrap: "wrap",
  height: `calc(100% - 16px)`,
  justifyContent: "center",
  paddingTop: "16px",
  width: "100%",
});

const LargeThumbnail = styled("img")({
  width: "100%",
  height: "auto",
  maxHeight: "100%",
  objectFit: "contain",
  position: "absolute",
  top: "50%",
  left: "50%",
  transform: "translate(-50%, -50%)",
  paddingBottom: "16px",
});

const getItemStyle = (isDragging, draggableStyle) => ({
  // styles we need to apply on draggables
  ...draggableStyle,

  ...(isDragging && {
    backgroundColor: "#C5C5C5",
  }),
});

const MediaItem = observer(({ children, video, index }) => {
  const store = useAppStore();
  const isPlayerPlaying = store.player.isPlaying;
  const playingVideo = store.playingVideo;

  const onMediaClicked = (media) => {
    if (!playingVideo || media.id !== playingVideo.id) {
      playerAPI.playMedia(media.id).catch(snackBarHandler(store));
      return;
    }
    playerAPI.pauseMedia().catch(snackBarHandler(store));
  };

  const renderAvatarState = (video) => {
    if (!playingVideo || video.id !== playingVideo.id) {
      return <Avatar alt={video.title} src={video.thumbnail} />;
    }
    const icon = isPlayerPlaying ? <VolumeUpIcon /> : <PlayArrowIcon />;
    return <Avatar>{icon}</Avatar>;
  };

  const downloadRatio = video.downloadRatio;
  return (
    <Draggable draggableId={video.id} index={index}>
      {(provided, snapshot) => (
        <>
          <ListItem
            ref={provided.innerRef}
            {...provided.draggableProps}
            {...provided.dragHandleProps}
            style={getItemStyle(
              snapshot.isDragging,
              provided.draggableProps.style
            )}
            button
            disableRipple
            autoFocus={playingVideo && video.id === playingVideo.id}
            onClick={() => onMediaClicked(video)}
            sx={
              playingVideo && video.id === playingVideo.id
                ? { backgroundColor: "rgba(246,250,254,1)" }
                : {}
            }
          >
            <Stack direction="column" spacing={1} sx={{ width: "100%" }}>
              <Stack direction="row" alignItems="center">
                <ListItemAvatar>{renderAvatarState(video)}</ListItemAvatar>
                <ListItemText primary={video.title} />
                <ListItemText
                  primary={durationToHMS(video.duration)}
                  sx={{
                    textAlign: "right",
                    minWidth: "max-content",
                    marginLeft: "8px",
                  }}
                />
              </Stack>
              {downloadRatio > 0 && downloadRatio < 1 && (
                <LinearProgress
                  value={downloadRatio * 100}
                  variant="determinate"
                />
              )}
            </Stack>
          </ListItem>
          {children}
        </>
      )}
    </Draggable>
  );
});

const PlayingMediaThumbnail = observer(() => {
  const store = useAppStore();
  const video = store.playingVideo;

  if (!video) {
    return null;
  }

  return (
    <LargeThumbnail
      src={video.thumbnail === null ? noPreview : video.thumbnail}
      alt={video.title}
    />
  );
});

const MainPlaylist = observer(() => {
  const store = useAppStore();
  const playlistId = store.player.queue;
  const videos = store.playlistVideos(playlistId);

  const onDragEnd = useCallback(
    (result) => {
      const { destination, source, draggableId } = result;

      if (
        !destination ||
        (destination.droppableId === source.droppableId &&
          destination.index === source.index)
      ) {
        return;
      }

      store.removePlaylistVideo(source.droppableId, draggableId);
      store.insertPlaylistVideo(
        destination.droppableId,
        draggableId,
        destination.index
      );

      const destPlaylist = store.playlists[destination.droppableId];
      const srcPlaylist = store.playlists[source.droppableId];
      playlistAPI
        .update(destination.droppableId, { ids: destPlaylist.ids })
        .catch(snackBarHandler(store));
      if (destination.dropppableId !== source.droppableId) {
        playlistAPI
          .update(source.droppableId, { ids: srcPlaylist.ids })
          .catch(snackBarHandler(store));
      }
    },
    [store]
  );

  const emptyPlaylist = () => {
    playlistAPI
      .update(store.playerPlaylist.id, { ids: [] })
      .catch(snackBarHandler(store));
  };

  if (!playlistId) {
    return null;
  }

  return (
    <DragDropContext onDragEnd={onDragEnd}>
      <Droppable droppableId={playlistId}>
        {(provided, _) => (
          <List
            ref={provided.innerRef}
            subheader={
              <ListSubheader>
                <Stack direction="row" alignItems="center">
                  <Typography sx={{ color: "#666666" }}>UP NEXT</Typography>
                  <IconButton
                    sx={{ marginLeft: "auto", paddingRight: "0px" }}
                    onClick={emptyPlaylist}
                  >
                    <ClearAllIcon />
                  </IconButton>
                </Stack>
              </ListSubheader>
            }
            sx={{ width: "100%", overflow: "auto" }}
          >
            {videos.map((video, index) => (
              <MediaItem video={video} index={index} key={video.id}>
                {index < videos.length - 1 && <Divider />}
              </MediaItem>
            ))}
            {provided.placeholder}
          </List>
        )}
      </Droppable>
    </DragDropContext>
  );
});

const HomePage = () => {
  return (
    <PageContainer>
      <MediaQuery minWidth={SIZES.large.min}>
        {(matches) =>
          matches ? (
            <Grid container justifyContent="center" sx={{ height: "100%" }}>
              <Grid item xs={8} sx={{ height: "100%" }}>
                <Container sx={{ height: "100%" }}>
                  <Stack direction="column" sx={{ height: "100%" }}>
                    <div
                      style={{
                        width: "100%",
                        marginBottom: "16px",
                      }}
                    >
                      <StreamInput />
                    </div>
                    <div style={{ position: "relative", height: "100%" }}>
                      <PlayingMediaThumbnail />
                    </div>
                  </Stack>
                </Container>
              </Grid>
              <Grid item xs={4} sx={{ height: "100%" }}>
                <Stack direction="row" sx={{ height: "100%" }}>
                  <Divider
                    orientation="vertical"
                    sx={{
                      backgroundColor: "#F0F0F0",
                    }}
                  />
                  <MainPlaylist />
                </Stack>
              </Grid>
            </Grid>
          ) : (
            <Stack sx={{ height: "100%", width: "100%" }}>
              <div
                style={{
                  width: "100%",
                  paddingLeft: "16px",
                  paddingRight: "16px",
                  marginBottom: "16px",
                  boxSizing: "border-box",
                }}
              >
                <StreamInput />
              </div>
              <MainPlaylist />
            </Stack>
          )
        }
      </MediaQuery>
    </PageContainer>
  );
};

export default HomePage;
