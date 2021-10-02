import React, { useCallback } from "react";

import {
  Grid,
  List,
  Divider,
  ListItem,
  ListItemText,
  ListItemAvatar,
  Avatar,
  MobileStepper,
  ListSubheader,
} from "@material-ui/core";
import { createStyles, makeStyles } from "@material-ui/core/styles";
import PlayArrowIcon from "@material-ui/icons/PlayArrow";
import VolumeUpIcon from "@material-ui/icons/VolumeUp";

import { DragDropContext, Draggable, Droppable } from "react-beautiful-dnd";

import { observer } from "mobx-react-lite";

import noPreview from "images/no-preview.png";
import playerAPI from "services/api/player";
import playlistAPI from "services/api/playlist";

import StreamInput from "components/stream_input";

import { useAppStore } from "components/app_context";

const useStyles = makeStyles(() =>
  createStyles({
    root: {
      display: "flex",
      flexWrap: "wrap",
      justifyContent: "center",
      overflow: "hidden",
      backgroundColor: "#F5F5F5",
    },
    gridList: {
      flexWrap: "nowrap",
      // Promote the list into his own layer on Chrome. This cost memory but
      // helps keeping high FPS.
      transform: "translateZ(0)",
    },
    gridItem: {
      minWidth: "160px",
    },
    title: {
      color: "#F5F5F5",
    },
    titleBar: {
      background:
        "linear-gradient(to top, rgba(0,0,0,0.7) 0%, rgba(0,0,0,0.3) 70%, rgba(0,0,0,0) 100%)",
    },
    playingVideoContainer: {
      textAlign: "center",
    },
    playingVideoThumbnail: {
      maxWidth: "75%",
    },
    videoDuration: {
      textAlign: "right",
    },
  })
);

const getListStyle = (isDraggingOver) => ({
  background: isDraggingOver ? "lightblue" : "#F5F5F5",
  maxHeight: "320px",
  overflow: "auto",
});
const getItemStyle = (isDragging, draggableStyle) => ({
  // styles we need to apply on draggables
  ...draggableStyle,

  ...(isDragging && {
    backgroundColor: "#C5C5C5",
  }),
});

const MediaItem = observer(({ children, video, index }) => {
  const classes = useStyles();
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

  const renderVideoDuration = (duration) => {
    const date = new Date(duration * 1000);
    const parts = [date.getUTCHours(), date.getUTCMinutes(), date.getSeconds()];
    let formatted_duration = "";

    parts.forEach((part) => {
      if (formatted_duration === "") {
        if (part === 0) {
          return;
        }
        formatted_duration = part.toString();
      } else {
        formatted_duration =
          formatted_duration + ":" + part.toString().padStart(2, "0");
      }
    });
    return (
      <ListItemText
        primary={formatted_duration}
        className={classes.videoDuration}
      />
    );
  };

  const downloadRatio = video.downloadRatio;
  return (
    <Draggable key={video.id} draggableId={video.id} index={index}>
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
            // autoFocus={video.id === playingVideo.id}
            onClick={() => onMediaClicked(video)}
          >
            <ListItemAvatar>{renderAvatarState(video)}</ListItemAvatar>
            <ListItemText primary={video.title} />
            {renderVideoDuration(video.duration)}
          </ListItem>
          {downloadRatio > 0 && downloadRatio < 1 && (
            <MobileStepper
              variant="progress"
              steps={100}
              position="static"
              activeStep={downloadRatio * 100}
              sx={{ flexGrow: 1 }}
            />
          )}
          {children}
        </>
      )}
    </Draggable>
  );
});

const HomePage = observer(() => {
  const classes = useStyles();
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
    <Grid container spacing={1}>
      <Grid item xs={12}>
        <StreamInput />
      </Grid>
      <Grid item xs={12} md={8} className={classes.playingVideoContainer}>
        {playingVideo && (
          <img
            className={classes.playingVideoThumbnail}
            src={
              playingVideo.thumbnail === null
                ? noPreview
                : playingVideo.thumbnail
            }
            alt={playingVideo.title}
          />
        )}
      </Grid>
      <Grid item xs={12} md={4}>
        {playlistId && (
          <DragDropContext onDragEnd={onDragEnd}>
            <Droppable droppableId={playlistId}>
              {(provided, snapshot) => (
                <List
                  style={getListStyle(snapshot.isDraggingOver)}
                  ref={provided.innerRef}
                  subheader={<ListSubheader>Lecture automatique</ListSubheader>}
                >
                  {videos.map((video, index) => (
                    <MediaItem video={video} index={index}>
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
  );
});

export default HomePage;
