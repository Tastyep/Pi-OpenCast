import React, { useEffect, useState } from "react";

import {
  Grid,
  Divider,
  IconButton,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  ListSubheader,
  TextField,
} from "@material-ui/core";
import DeleteIcon from "@material-ui/icons/Delete";
import PauseIcon from "@material-ui/icons/Pause";
import PlayArrowIcon from "@material-ui/icons/PlayArrow";

import { observer } from "mobx-react-lite";

import { Draggable, Droppable } from "react-beautiful-dnd";

import playerAPI from "services/api/player";
import playlistAPI from "services/api/playlist";
import { useAppStore } from "./app_context";

// const getListStyle = isDraggingOver => ({
//   backgorund: isDraggingOver ? 'lightblue' : '#F5F5F5',
// });
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

const subheaderStyle = {
  backgroundColor: "#FFFFFF",
};

const Playlist = observer(({ playlistId }) => {
  const store = useAppStore();
  const videos = store.playlistVideos(playlistId);
  const playlist = store.playlists[playlistId];
  const activeVideoId = store.player.videoId;
  const isPlayerPlaying = store.player.isPlaying;
  const [name, setName] = useState("");

  useEffect(() => {
    setName(playlist.name);
  }, [playlist.name]);

  const renamePlaylist = (event) => {
    if (!event) {
      return;
    }
    event.preventDefault();
    playlistAPI
      .update(playlistId, { name: name })
      .catch((error) => console.log(error));
    return;
  };

  const removePlaylist = () => {
    playlistAPI.delete_(playlistId).catch((error) => console.log(error));
  };

  const onMediaClicked = (media) => {
    if (media.id !== activeVideoId) {
      playerAPI
        .playMedia(media.id, playlistId)
        .catch((error) => console.log(error));
      return;
    }
    playerAPI.pauseMedia().catch((error) => console.log(error));
  };

  const renderButtonState = (video) => {
    if (video.id === activeVideoId) {
      const icon = isPlayerPlaying ? <PauseIcon /> : <PlayArrowIcon />;
      return <ListItemIcon>{icon}</ListItemIcon>;
    }
  };

  const renderMediaItem = (video, index) => {
    if (!video) {
      return;
    }
    return (
      <Draggable draggableId={video.id} index={index} key={video.id}>
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
              autoFocus={video.id === activeVideoId}
              onClick={() => onMediaClicked(video)}
            >
              {renderButtonState(video)}
              <ListItemText primary={video.title} />
            </ListItem>
            {index < videos.length - 1 && <Divider />}
          </>
        )}
      </Draggable>
    );
  };

  return (
    <Droppable droppableId={playlistId}>
      {(provided, snapshot) => (
        <List
          subheader={
            <ListSubheader style={subheaderStyle}>
              <form
                onSubmit={(e) => renamePlaylist(e)}
                noValidate
                autoComplete="off"
              >
                <Grid container>
                  <Grid item xs={11}>
                    {(store.playlists[playlistId].name === "Home" && (
                      <b>{name}</b>
                    )) || (
                      <TextField
                        value={name}
                        onChange={(e) => setName(e.target.value)}
                      />
                    )}
                  </Grid>
                  {! store.playlists[playlistId].generated && (
                    <Grid item xs={1}>
                      <IconButton onClick={() => removePlaylist()}>
                        <DeleteIcon />
                      </IconButton>
                    </Grid>
                  )}
                </Grid>
              </form>
            </ListSubheader>
          }
          style={getListStyle(snapshot.isDraggingOver)}
          ref={provided.innerRef}
        >
          {videos.map((video, index) => renderMediaItem(video, index))}
          {provided.placeholder}
        </List>
      )}
    </Droppable>
  );
});

export default Playlist;
