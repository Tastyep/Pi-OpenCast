import { useState } from "react";

import {
  IconButton,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Menu,
  MenuItem,
  Stack,
  Typography,
} from "@mui/material";
import AddIcon from "@mui/icons-material/Add";
import MoreVertIcon from "@mui/icons-material/MoreVert";
import DeleteIcon from "@mui/icons-material/Delete";

import { styled } from "@mui/material/styles";

import { Link } from "react-router-dom";

import { observer } from "mobx-react-lite";

import playlistAPI from "services/api/playlist";
import snackBarHandler from "services/api/error";

import { useAppStore } from "components/app_context";
import PlaylistThumbnail from "components/playlist_thumbnail";
import PlaylistModal from "components/playlist_modal";

const PlaylistItemContainer = styled(ListItem)({
  flexGrow: 0,
  flowShrink: 1,
  flexBasis: "256px",
  flexDirection: "column",
  maxWidth: "50%",
});

const PlaylistItemBar = styled((props) => <Stack {...props} />)({
  flexDirection: "row",
  alignItems: "center",
  justifyContent: "center",
  width: "100%",
  position: "relative",
  transform: "translate(0px, -40px)",
  marginBottom: "-40px",
  backgroundColor: "rgba(0, 0, 0, 0.6)",
  borderBottomLeftRadius: "8px",
  borderBottomRightRadius: "8px",
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
    playlistAPI.delete_(playlist.id).catch(snackBarHandler(store));
  };

  return (
    <PlaylistItemContainer>
      <Link
        to={"/playlists/" + playlist.id}
        style={{ width: "100%", aspectRatio: "1/1" }}
      >
        <PlaylistThumbnail videos={store.playlistVideos(playlist.id)} />
      </Link>
      <PlaylistItemBar>
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
      </PlaylistItemBar>
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
    </PlaylistItemContainer>
  );
};

const PlaylistsPage = observer(() => {
  const store = useAppStore();
  const playlists = Object.values(store.playlists);

  const [open, setOpen] = useState(false);

  playlists.sort((a, b) => {
    return a.name.localeCompare(b.name);
  });
  return (
    <>
      <PlaylistModal open={open} close={() => setOpen(false)} />
      <List sx={{ display: "flex", flexDirection: "row", flexWrap: "wrap" }}>
        <PlaylistItemContainer>
          <IconButton
            sx={{
              width: "100%",
              height: "100%",
              backgroundColor: "#F0F0F0",
              borderRadius: "8px",
            }}
            onClick={() => setOpen(true)}
          >
            <AddIcon sx={{ height: "25%", width: "25%" }} />
          </IconButton>
          <PlaylistItemBar sx={{ height: "40px" }}>
            <Typography sx={{ color: "#FFFFFF" }}>New playlist</Typography>
          </PlaylistItemBar>
        </PlaylistItemContainer>
        {playlists.map((playlist, _) => (
          <PlaylistItem key={playlist.id} playlist={playlist} />
        ))}
      </List>
    </>
  );
});

export default PlaylistsPage;
