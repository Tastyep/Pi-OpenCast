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
import PlayArrowIcon from "@mui/icons-material/PlayArrow";
import VolumeUpIcon from "@mui/icons-material/VolumeUp";

import { DragDropContext, Draggable, Droppable } from "react-beautiful-dnd";

import { observer } from "mobx-react-lite";

import Media from "react-media";
import { SIZES } from "constants.js";

import noPreview from "images/no-preview.png";
import playerAPI from "services/api/player";
import playlistAPI from "services/api/playlist";
import { duration_to_hms } from "services/duration";

import { useAppStore } from "components/app_context";
import StreamInput from "components/stream_input";

const PageContainer = styled("div")({
  display: "flex",
  flexWrap: "wrap",
  height: `calc(100% - 16px)`,
  justifyContent: "center",
  paddingTop: "16px",
  backgroundColor: "#F5F5F5",
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
  const playingVideo = store.playingVideo();
  const playlistId = store.player.queue;

  const onMediaClicked = (media) => {
    if (!playingVideo || media.id !== playingVideo.id) {
      playerAPI
        .playMedia(media.id, playlistId)
        .catch((error) => console.log(error));
      return;
    }
    playerAPI.pauseMedia().catch((error) => console.log(error));
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
            onClick={() => onMediaClicked(video)}
          >
            <Stack direction="column" spacing={1} sx={{ width: "100%" }}>
              <Stack direction="row" alignItems="center">
                <ListItemAvatar>{renderAvatarState(video)}</ListItemAvatar>
                <ListItemText primary={video.title} />
                <ListItemText
                  primary={duration_to_hms(video.duration)}
                  sx={{ textAlign: "right", minWidth: "max-content" }}
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

const HomePage = observer(() => {
  const store = useAppStore();
  const playlistId = store.player.queue;
  const videos = store.playlistVideos(playlistId);
  const playingVideo = store.playingVideo();

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
      playlistAPI.update(destination.droppableId, { ids: destPlaylist.ids });
      if (destination.dropppableId !== source.droppableId) {
        playlistAPI.update(source.droppableId, { ids: srcPlaylist.ids });
      }
    },
    [store]
  );

  return (
    <PageContainer>
      <Media queries={{ large: { minWidth: SIZES.large.min } }}>
        {(matches) =>
          matches.large ? (
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
                      {playingVideo && (
                        <LargeThumbnail
                          src={
                            playingVideo.thumbnail === null
                              ? noPreview
                              : playingVideo.thumbnail
                          }
                          alt={playingVideo.title}
                        />
                      )}
                    </div>
                  </Stack>
                </Container>
              </Grid>
              <Grid item xs={4} sx={{ height: "100%", overflow: "auto" }}>
                {playlistId && (
                  <DragDropContext onDragEnd={onDragEnd}>
                    <Droppable droppableId={playlistId}>
                      {(provided, snapshot) => (
                        <List
                          ref={provided.innerRef}
                          subheader={
                            <ListSubheader>Lecture automatique</ListSubheader>
                          }
                        >
                          {videos.map((video, index) => (
                            <MediaItem
                              video={video}
                              index={index}
                              key={video.id}
                            >
                              {index < videos.length - 1 && <Divider />}
                            </MediaItem>
                          ))}
                          {provided.placeholder}
                        </List>
                      )}
                    </Droppable>
                  </DragDropContext>
                )}
              </Grid>
            </Grid>
          ) : (
            <Stack sx={{ height: "100%" }}>
              <div
                style={{
                  width: "100%",
                  marginBottom: "16px",
                }}
              >
                <StreamInput />
              </div>
              <div style={{ overflow: "auto" }}>
                {playlistId && (
                  <DragDropContext onDragEnd={onDragEnd}>
                    <Droppable droppableId={playlistId}>
                      {(provided, snapshot) => (
                        <List
                          ref={provided.innerRef}
                          subheader={
                            <ListSubheader>Lecture automatique</ListSubheader>
                          }
                        >
                          {videos.map((video, index) => (
                            <MediaItem
                              video={video}
                              index={index}
                              key={video.id}
                            >
                              {index < videos.length - 1 && <Divider />}
                            </MediaItem>
                          ))}
                          {provided.placeholder}
                        </List>
                      )}
                    </Droppable>
                  </DragDropContext>
                )}
              </div>
            </Stack>
          )
        }
      </Media>
    </PageContainer>
  );
});

export default HomePage;
