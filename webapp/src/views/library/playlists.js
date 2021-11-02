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
import PlaylistPlayIcon from "@mui/icons-material/PlaylistPlay";
import QueueMusicIcon from "@mui/icons-material/QueueMusic";
import ShuffleIcon from "@mui/icons-material/Shuffle";

import { styled } from "@mui/material/styles";

import { Link } from "react-router-dom";

import { observer } from "mobx-react-lite";

import { queueNext, queueLast, shuffleIds } from "services/playlist";
import playlistAPI from "services/api/playlist";
import playerAPI from "services/api/player";
import snackBarHandler from "services/api/error";

import { useAppStore } from "components/app_context";
import PlaylistThumbnail from "components/playlist_thumbnail";
import PlaylistModal from "components/playlist_modal";

const PlaylistItemContainer = styled(ListItem)({
  flexGrow: 0,
  flowShrink: 1,
  flexBasis: "256px",
  flexDirection: "column",
  maxWidth: `calc(50% - 8px)`, // Remove the gap between items
  padding: "0px 0px",
});

const PlaylistItemBar = styled((props) => <Stack {...props} />)({
  flexDirection: "row",
  alignItems: "center",
  justifyContent: "center",
  width: "100%",
  height: "40px",
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

  const shufflePlayNext = () => {
    closeMenu();

    const playlistIds = queueNext(
      store.playerPlaylist,
      store.player.videoId,
      shuffleIds(playlist.ids)
    );
    playlistAPI
      .update(store.playerPlaylist.id, { ids: playlistIds })
      .then((_) => {
        if (store.player.isStopped) {
          playerAPI.playMedia(playlistIds[0]).catch(snackBarHandler(store));
        }
      })
      .catch(snackBarHandler(store));
  };

  const playNext = () => {
    closeMenu();
    const playlistIds = queueNext(
      store.playerPlaylist,
      store.player.videoId,
      playlist.ids
    );
    playlistAPI
      .update(store.playerPlaylist.id, { ids: playlistIds })
      .then((_) => {
        if (store.player.isStopped) {
          playerAPI.playMedia(playlistIds[0]).catch(snackBarHandler(store));
        }
      })
      .catch(snackBarHandler(store));
  };

  const queue = () => {
    closeMenu();
    const playlistIds = queueLast(
      store.playerPlaylist,
      store.player.videoId,
      playlist.ids
    );
    playlistAPI
      .update(store.playerPlaylist.id, { ids: playlistIds })
      .then((_) => {
        store.enqueueSnackbar({
          message: playlist.name + " queued",
          options: {
            variant: "success",
          },
        });
      })
      .catch(snackBarHandler(store));
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
        <div
          style={{ width: "40px", marginRight: "auto", visibility: "hidden" }}
        ></div>
        <Typography
          sx={{ color: "#FFFFFF", whiteSpace: "nowrap", overflow: "hidden" }}
        >
          {playlist.name}
        </Typography>
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
        <MenuItem onClick={() => shufflePlayNext(playlist)}>
          <ListItemIcon>
            <ShuffleIcon />
          </ListItemIcon>
          <ListItemText>Shuffle play</ListItemText>
        </MenuItem>
        <MenuItem onClick={() => playNext()}>
          <ListItemIcon>
            <PlaylistPlayIcon />
          </ListItemIcon>
          <ListItemText>Play next</ListItemText>
        </MenuItem>
        <MenuItem onClick={() => queue()}>
          <ListItemIcon>
            <QueueMusicIcon />
          </ListItemIcon>
          <ListItemText>Add to queue</ListItemText>
        </MenuItem>
        <MenuItem onClick={() => removePlaylist()}>
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
      <List
        sx={{
          display: "flex",
          flexDirection: "row",
          flexWrap: "wrap",
          gap: "8px 16px",
        }}
      >
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
          <PlaylistItemBar>
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
