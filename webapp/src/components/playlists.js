import React, { useState } from "react";

import { Grid, IconButton, TextField, Divider, List, ListItem, ListItemText, ListSubheader} from "@material-ui/core";
import AddCircleOutlineIcon from '@material-ui/icons/AddCircleOutline';
import DeleteIcon from '@material-ui/icons/Delete';

import { observer } from "mobx-react-lite";

import { useAppStore } from "./app_context";
import playlistAPI from "services/api/playlist"

const Playlists = observer(() => {
  const store = useAppStore()

  return (
    <div>
      <PlaylistInput />
      <Grid container spacing={2}>
      { store.playlists.map((playlist) => (
        <Grid item key={playlist.id}>
          <Playlist playlist={playlist} />
        </Grid>
      ))}
      </Grid>
    </div>
  )
})

const PlaylistInput = () => {
  const [name, setName] = useState("")

  const addPlaylist = () => {
    playlistAPI.create({name: name})
      .catch((error) => console.log(error));
    setName("")
  }

  return (
    <Grid container>
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
        <IconButton
          onClick={() => addPlaylist()} 
        >
          <AddCircleOutlineIcon />
        </IconButton>
      </Grid>
    </Grid>
  )
}

const Playlist = ({playlist}) => {
  const store = useAppStore()
  const videos = store.playlistVideos(playlist.id)

  const removePlaylist = () => {
    playlistAPI
      .delete_(playlist.id)
      .catch((error) => console.log(error));
  }

  return (
    <>
      <List subheader={
        <ListSubheader>
          {playlist.name}
          <IconButton
            onClick={() => removePlaylist()}
          >
            <DeleteIcon />
          </IconButton>
        </ListSubheader>
      }>
      { videos.map((video) => (
        <div key={video.id}>
          <ListItem>
            <ListItemText primary={video.title} />
          </ListItem>
          <Divider variant="inset" component="li" />
        </div>
       ))}
      </List>
    </>
  )
}

export default Playlists
