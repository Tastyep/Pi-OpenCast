import {
  Divider,
  IconButton,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  ListSubheader,
} from "@material-ui/core";
import DeleteIcon from "@material-ui/icons/Delete";
import PauseIcon from "@material-ui/icons/Pause";
import PlayArrowIcon from "@material-ui/icons/PlayArrow";
import {observer} from "mobx-react-lite";
import React from "react";
import {Draggable, Droppable} from "react-beautiful-dnd";
import playerAPI from "services/api/player";
import playlistAPI from "services/api/playlist";

import {useAppStore} from "./app_context";

// const getListStyle = isDraggingOver => ({
//   backgorund: isDraggingOver ? 'lightblue' : '#F5F5F5',
// });
const getListStyle = (isDraggingOver) => ({
  background : isDraggingOver ? "lightblue" : "#F5F5F5",
  maxHeight : "320px",
  overflow : "auto",
});
const getItemStyle = (isDragging, draggableStyle) => ({
  // styles we need to apply on draggables
  ...draggableStyle,

  ...(isDragging && {
    backgroundColor : "#C5C5C5",
  }),
});

const subheaderStyle = {
  backgroundColor : "#FFFFFF",
};

const Playlist = observer(({ playlist }) => {
  const store = useAppStore();
  const videos = store.playlistVideos(playlist.id);
  const player = store.player;
  const activeVideoId = store.player.videoId;
  const isPlayerPlaying = player.isPlaying;

  const removePlaylist = () => {
    playlistAPI.delete_(playlist.id).catch((error) => console.log(error));
  };

  const onMediaClicked = (media, playlist) => {
    if (media.id !== activeVideoId) {
      playerAPI.playMedia(media.id, playlist.id)
          .catch((error) => console.log(error));
      return;
    }
    playerAPI.pauseMedia().catch((error) => console.log(error));
  };

  const renderButtonState = (video) => {
    if (video.id === activeVideoId) {
      const icon = isPlayerPlaying ? <PauseIcon />: <PlayArrowIcon />;
      return <ListItemIcon>{icon}<
          /ListItemIcon>;
    }
  };

  const renderMediaItem = (video, playlist, index) => {
    if (video) {
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
                onClick={() => onMediaClicked(video, playlist)}
              >
                {renderButtonState(video)}
                <ListItemText primary={video.title} />
          </ListItem>
              {index < videos.length - 1 && <Divider />
    }
            </>
          )}
        </Draggable>
      );
  }
  };

  return (
    <Droppable droppableId={playlist.id}>
      {(provided, snapshot) => (
        <List
          subheader={
            <ListSubheader style={subheaderStyle}>
              <b>{playlist.name}</b>
              {playlist.id !== store.playlists[0].id && (
                <IconButton onClick={() => removePlaylist()}>
                  <DeleteIcon />
                </IconButton>
              )}
            </ListSubheader>
          }
          style={getListStyle(snapshot.isDraggingOver)}
          ref={provided.innerRef}
        >
          {videos.map((video, index) => renderMediaItem(video, playlist, index))}
          {provided.placeholder}
        </List>
      )}
    </Droppable>
  );
});

export default Playlist;
