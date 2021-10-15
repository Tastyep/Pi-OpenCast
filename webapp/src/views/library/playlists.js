import { useState } from "react";

import {
  Box,
  Button,
  IconButton,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Menu,
  MenuItem,
  Modal,
  Stack,
  TextField,
  Typography,
} from "@mui/material";
import AddIcon from "@mui/icons-material/Add";
import MoreVertIcon from "@mui/icons-material/MoreVert";
import DeleteIcon from "@mui/icons-material/Delete";

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

  const [anchor, setAnchor] = useState(null);
  const isMenuOpen = Boolean(anchor);

  const closeMenu = () => {
    setAnchor(null);
  };
  const removePlaylist = (playlist) => {
    closeMenu();
    playlistAPI.delete_(playlist.id).catch((error) => console.log(error));
  };

  return (
    <>
      <ListItem sx={{ flex: 0, flexDirection: "column" }}>
        <Link
          to={"/playlists/" + playlist.id}
          style={{
            display: "flex",
            height: "256px",
            width: "256px",
          }}
        >
          <PlaylistThumbnail videos={store.playlistVideos(playlist.id)} />
        </Link>
        <Stack
          direction="row"
          alignItems="center"
          justifyContent="center"
          sx={{
            position: "relative",
            bottom: "40px",
            backgroundColor: "rgba(0, 0, 0, 0.6)",
            width: "256px",
            borderBottomLeftRadius: "12px",
            borderBottomRightRadius: "12px",
          }}
        >
          <div style={{ marginRight: "auto", visibility: "hidden" }}></div>
          <div style={{ marginRight: "auto", visibility: "hidden" }}></div>
          <div style={{ marginRight: "auto", visibility: "hidden" }}></div>
          <Typography sx={{ color: "#FFFFFF" }}>{playlist.name}</Typography>
          <div style={{ marginRight: "auto", visibility: "hidden" }}></div>
          <IconButton
            sx={{ marginLeft: "auto" }}
            onClick={(e) => {
              setAnchor(e.currentTarget);
            }}
          >
            <MoreVertIcon sx={{ marginLeft: "auto", color: "#FFFFFF" }} />
          </IconButton>
        </Stack>
      </ListItem>
      <Menu
        id="media-menu"
        anchorEl={anchor}
        open={isMenuOpen}
        onClose={closeMenu}
        MenuListProps={{
          "aria-labelledby": "basic-button",
        }}
        transformOrigin={{ horizontal: "right", vertical: "top" }}
        anchorOrigin={{ horizontal: "right", vertical: "bottom" }}
      >
        <MenuItem onClick={() => removePlaylist(playlist)}>
          <ListItemIcon>
            <DeleteIcon />
          </ListItemIcon>
          <ListItemText>Delete playlist</ListItemText>
        </MenuItem>
      </Menu>
    </>
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
          <Stack
            direction="row"
            alignItems="center"
            justifyContent="center"
            sx={{
              position: "relative",
              bottom: "40px",
              backgroundColor: "rgba(0, 0, 0, 0.6)",
              width: "256px",
              height: "40px",
              borderBottomLeftRadius: "12px",
              borderBottomRightRadius: "12px",
            }}
          >
            <Typography sx={{ color: "#FFFFFF" }}>New playlist</Typography>
          </Stack>
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
