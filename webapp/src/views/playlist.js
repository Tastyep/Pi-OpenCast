import { useState } from "react";

import { Box, Button, Divider, List, Stack, Typography } from "@mui/material";
import IconButton from "@mui/material/IconButton";
import ListItemIcon from "@mui/material/ListItemIcon";
import ListItemText from "@mui/material/ListItemText";
import Menu from "@mui/material/Menu";
import MenuItem from "@mui/material/MenuItem";
import Modal from "@mui/material/Modal";
import TextField from "@mui/material/TextField";

import EditIcon from "@mui/icons-material/Edit";
import ShuffleIcon from "@mui/icons-material/Shuffle";
import DeleteIcon from "@mui/icons-material/Delete";
import PlaylistPlayIcon from "@mui/icons-material/PlaylistPlay";
import QueueMusicIcon from "@mui/icons-material/QueueMusic";
import MoreVertIcon from "@mui/icons-material/MoreVert";

import { styled } from "@mui/material/styles";

import { useParams } from "react-router-dom";

import { observer } from "mobx-react-lite";

import { queueNext, queueLast, shuffleIds } from "services/playlist";
import playlistAPI from "services/api/playlist";
import playerAPI from "services/api/player";
import snackBarHandler from "services/api/error";

import { useAppStore } from "components/app_context";
import PlaylistThumbnail from "components/playlist_thumbnail";
import MediaItem from "components/media_item";

const pluralize = require("pluralize");

const ModalContent = styled(Box)({
  position: "absolute",
  top: "50%",
  left: "50%",
  transform: "translate(-50%, -50%)",
  width: 400,
  maxWidth: "75%",
  backgroundColor: "#FFFFFF",
  border: "2px solid #000",
  boxShadow: 24,

  p: 4,
  padding: "16px",
});

const UpdateModal = (props) => {
  const store = useAppStore();

  const { open, close, playlist } = props;
  const [name, setName] = useState(playlist.name);

  const updatePlaylist = () => {
    playlistAPI
      .update(playlist.id, { name: name })
      .catch(snackBarHandler(store));
    close();
  };

  return (
    <Modal open={open} onClose={close}>
      <ModalContent>
        <Typography variant="h6" sx={{ marginBottom: "8px" }}>
          {playlist.name}
        </Typography>
        <TextField
          id="standard-basic"
          label="Title"
          variant="standard"
          defaultValue={playlist.name}
          autoFocus
          sx={{ width: "100%" }}
          onChange={(e) => setName(e.target.value)}
        />
        <div
          style={{
            display: "flex",
            justifyContent: "end",
            marginTop: "24px",
          }}
        >
          <Button variant="text" onClick={close}>
            Cancel
          </Button>
          <Button variant="contained" onClick={() => updatePlaylist()}>
            Save
          </Button>
        </div>
      </ModalContent>
    </Modal>
  );
};

const PlaylistMenu = (props) => {
  const store = useAppStore();
  const { open, anchorEl, playlist, closeMenu } = props;

  const playNext = (playlist) => {
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

  const queue = (playlist) => {
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
    playlistAPI
      .delete_(playlist.id)
      .then((_) => {
        window.location.href = "/library/playlists";
      })
      .catch(snackBarHandler(store));
  };

  return (
    <Menu
      id="playlist-menu"
      anchorEl={anchorEl}
      open={open}
      onClose={closeMenu}
      MenuListProps={{
        "aria-labelledby": "basic-button",
      }}
      transformOrigin={{ horizontal: "right", vertical: "top" }}
      anchorOrigin={{ horizontal: "right", vertical: "bottom" }}
    >
      <MenuItem onClick={() => playNext(playlist)}>
        <ListItemIcon>
          <PlaylistPlayIcon />
        </ListItemIcon>
        <ListItemText>Play next</ListItemText>
      </MenuItem>
      <MenuItem onClick={() => queue(playlist)}>
        <ListItemIcon>
          <QueueMusicIcon />
        </ListItemIcon>
        <ListItemText>Add to queue</ListItemText>
      </MenuItem>
      <MenuItem onClick={() => removePlaylist(playlist)}>
        <ListItemIcon>
          <DeleteIcon />
        </ListItemIcon>
        <ListItemText>Delete playlist</ListItemText>
      </MenuItem>
    </Menu>
  );
};

const PlaylistPage = observer(() => {
  const store = useAppStore();
  const { id } = useParams();

  const [isModalOpen, setModalOpen] = useState(false);
  const [anchor, setAnchor] = useState(null);
  const isMenuOpen = Boolean(anchor);

  const playlist = store.playlists[id];
  const videos = store.playlistVideos(id);

  const shufflePlayNext = (playlist) => {
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

  if (!playlist) {
    return null;
  }

  return (
    <Box sx={{ display: "flex", flexDirection: "column", height: "100%" }}>
      <UpdateModal
        open={isModalOpen}
        close={() => setModalOpen(false)}
        playlist={playlist}
      />
      <Box
        sx={{
          display: "flex",
          flexDirection: "row",
          alignItems: "center",
          marginTop: "32px",
          marginBottom: "32px",
          marginLeft: "16px",
        }}
      >
        <Box sx={{ marginRight: "32px", height: 128, width: 128 }}>
          <PlaylistThumbnail videos={videos} />
        </Box>
        <Box>
          <Typography variant="h4">{playlist.name}</Typography>
          <Typography>{pluralize("media", videos.length, true)}</Typography>
          <Stack direction="row" alignItems="center" sx={{ marginTop: "16px" }}>
            <Box>
              <Button
                variant="contained"
                startIcon={<ShuffleIcon />}
                sx={{ alignItems: "flex-start", marginRight: "8px" }}
                onClick={() => shufflePlayNext(playlist)}
              >
                Shuffle
              </Button>
              <Button
                variant="outlined"
                startIcon={<EditIcon />}
                sx={{ alignItems: "flex-start" }}
                onClick={() => setModalOpen(true)}
              >
                Edit playlist
              </Button>
            </Box>
            <IconButton
              aria-controls="playlist-menu"
              aria-haspopup="true"
              aria-expanded={isMenuOpen ? "true" : undefined}
              onClick={(e) => setAnchor(e.currentTarget)}
            >
              <MoreVertIcon />
            </IconButton>
            <PlaylistMenu
              open={isMenuOpen}
              anchorEl={anchor}
              playlist={playlist}
              closeMenu={() => setAnchor(null)}
            />
          </Stack>
        </Box>
      </Box>
      <Divider />
      <Box
        sx={{
          height: "100%",
          width: "100%",
          overflow: "auto",
        }}
      >
        <List sx={{ height: "100%", width: "100%", padding: "0px" }}>
          {videos.map((video) => (
            <MediaItem key={video.id} playlist={playlist} video={video} />
          ))}
        </List>
      </Box>
    </Box>
  );
});

export default PlaylistPage;
