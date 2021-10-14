import { useState } from "react";

import {
  Box,
  Button,
  IconButton,
  List,
  ListItem,
  Modal,
  TextField,
  Typography,
} from "@mui/material";
import AddIcon from "@mui/icons-material/Add";
import { styled } from "@mui/material/styles";

import { Link } from "react-router-dom";

import { observer } from "mobx-react-lite";

import { useAppStore } from "components/app_context";
import playlistAPI from "services/api/playlist";
import PlaylistThumbnail from "components/playlist_thumbnail";

const ModalContent = styled(Box)({
  position: "absolute",
  top: "50%",
  left: "50%",
  transform: "translate(-50%, -50%)",
  width: 400,
  backgroundColor: "#FFFFFF",
  border: "2px solid #000",
  boxShadow: 24,

  p: 4,
  padding: "16px",
});

const PlaylistItem = ({ playlist }) => {
  const store = useAppStore();

  return (
    <ListItem sx={{ flex: 0, flexDirection: "column" }}>
      <Link
        to={"/playlists/" + playlist.id}
        style={{
          display: "flex",
          height: 256,
          width: 256,
        }}
      >
        <PlaylistThumbnail videos={store.playlistVideos(playlist.id)} />
      </Link>
      <Typography sx={{ marginTop: "16px" }}>{playlist.name}</Typography>
    </ListItem>
  );
};

const PlaylistsPage = observer(() => {
  const store = useAppStore();
  const [open, setOpen] = useState(false);
  const [title, setTitle] = useState("");

  const createPlaylist = () => {
    playlistAPI.create({ name: title }).catch((error) => console.log(error));
    setOpen(false);
  };

  return (
    <>
      <Modal open={open} onClose={() => setOpen(false)}>
        <ModalContent>
          <Typography variant="h6" sx={{ marginBottom: "8px" }}>
            New playlist
          </Typography>
          <TextField
            id="standard-basic"
            label="Title"
            variant="standard"
            sx={{ width: "100%" }}
            onChange={(e) => setTitle(e.target.value)}
          />
          <div
            style={{
              display: "flex",
              justifyContent: "end",
              marginTop: "24px",
            }}
          >
            <Button variant="text" onClick={() => setOpen(false)}>
              Cancel
            </Button>
            <Button variant="contained" onClick={() => createPlaylist()}>
              Save
            </Button>
          </div>
        </ModalContent>
      </Modal>
      <List sx={{ display: "flex", flexWrap: "wrap" }}>
        <ListItem sx={{ flex: 0, flexDirection: "column" }}>
          <IconButton
            sx={{
              height: "256px",
              width: "256px",
              backgroundColor: "#F0F0F0",
              borderRadius: "5%",
            }}
            onClick={() => setOpen(true)}
          >
            <AddIcon sx={{ height: "25%", width: "25%" }} />
          </IconButton>
          <Typography sx={{ marginTop: "16px" }}>New playlist</Typography>
        </ListItem>
        {Object.keys(store.playlists).map((playlistId, _) => (
          <PlaylistItem
            key={playlistId}
            playlist={store.playlists[playlistId]}
          />
        ))}
      </List>
    </>
  );
});

export default PlaylistsPage;
