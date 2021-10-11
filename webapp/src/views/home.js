import React, { useCallback } from "react";

import { styled } from "@mui/material/styles";

import {
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
  height: "100%",
  justifyContent: "center",
  overflow: "hidden",
  backgroundColor: "#F5F5F5",
});

const LargeThumbnail = styled("img")({
  width: "90%",
  height: "auto",
  maxHeight: "100%",
  objectFit: "contain",
  position: "absolute",
  top: "50%",
  left: "50%",
  transform: "translate(-50%, -50%)",
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
      <div style={{ marginTop: "8px", marginBottom: "16px", width: "80%" }}>
        <StreamInput />
      </div>
      <Media queries={{ large: { minWidth: SIZES.large.min } }}>
        {(matches) =>
          matches.large ? (
            <Grid
              container
              justifyContent="center"
              sx={{ height: `calc(100% - 72px)` }}
            >
              <Grid item xs={8} sx={{ height: "100%", position: "relative" }}>
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
                          <MediaItem video={video} index={index} key={video.id}>
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
          )
        }
      </Media>
    </PageContainer>
  );
});

export default HomePage;
