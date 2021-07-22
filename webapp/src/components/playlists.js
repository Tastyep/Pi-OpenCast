import React, { useState, useCallback } from "react";

import { Grid, IconButton, TextField } from "@material-ui/core";
import AddCircleOutlineIcon from "@material-ui/icons/AddCircleOutline";

import { observer } from "mobx-react-lite";

import { DragDropContext } from "react-beautiful-dnd";

import { useAppStore } from "./app_context";
import playlistAPI from "services/api/playlist";
import Playlist from "./playlist";

const Playlists = observer(() => {
  const store = useAppStore();

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
    <div>
      <PlaylistInput />
      <DragDropContext onDragEnd={onDragEnd}>
        <Grid container spacing={2}>
          {Object.keys(store.playlists).map((playlistId, _) => (
            <Grid item key={playlistId} xs={12} sm={6} md={6} lg={4} xl={3}>
              <Playlist playlistId={playlistId} />
            </Grid>
          ))}
        </Grid>
      </DragDropContext>
    </div>
  );
});

const playlistInputStyle = {
  paddingBottom: "16px",
};

const PlaylistInput = () => {
  const [name, setName] = useState("");

  const addPlaylist = () => {
    playlistAPI.create({ name: name }).catch((error) => console.log(error));
    setName("");
  };

  return (
    <Grid container style={playlistInputStyle}>
      <Grid item>
        <TextField
          fullWidth
          id="outlined-basic"
          label="New Playlist"
          variant="standard"
          value={name}
          onChange={(e) => setName(e.target.value)}
        />
      </Grid>
      <Grid item>
        <IconButton onClick={() => addPlaylist()}>
          <AddCircleOutlineIcon />
        </IconButton>
      </Grid>
    </Grid>
  );
};

export default Playlists;
