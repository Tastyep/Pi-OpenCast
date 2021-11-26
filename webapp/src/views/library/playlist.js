import React, { useState } from "react";

import Box from "@mui/material/Box";
import Button from "@mui/material/Button";
import Collapse from "@mui/material/Collapse";
import IconButton from "@mui/material/IconButton";
import List from "@mui/material/List";
import ListItemIcon from "@mui/material/ListItemIcon";
import ListItemText from "@mui/material/ListItemText";
import Menu from "@mui/material/Menu";
import MenuItem from "@mui/material/MenuItem";
import Modal from "@mui/material/Modal";
import Stack from "@mui/material/Stack";
import TextField from "@mui/material/TextField";
import Typography from "@mui/material/Typography";

import EditIcon from "@mui/icons-material/Edit";
import ExpandLessIcon from "@mui/icons-material/ExpandLess";
import ExpandMoreIcon from "@mui/icons-material/ExpandMore";
import ShuffleIcon from "@mui/icons-material/Shuffle";
import DeleteIcon from "@mui/icons-material/Delete";
import PlaylistPlayIcon from "@mui/icons-material/PlaylistPlay";
import PlaylistAddIcon from "@mui/icons-material/PlaylistAdd";
import QueueMusicIcon from "@mui/icons-material/QueueMusic";
import MoreVertIcon from "@mui/icons-material/MoreVert";

import { styled } from "@mui/material/styles";

import { useParams, useNavigate } from "react-router-dom";

import { useMediaQuery } from "react-responsive";

import { observer } from "mobx-react-lite";

import { queueNext, queueLast, shuffleIds } from "services/playlist";
import playlistAPI from "services/api/playlist";
import playerAPI from "services/api/player";
import snackBarHandler from "services/api/error";
import { humanReadableDuration } from "services/duration";

import { useAppStore } from "components/app_context";
import PlaylistThumbnail from "components/playlist_thumbnail";
import { MediaItem } from "components/media_item";
import { VirtualizedMediaList } from "components/media_list";

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
  const navigate = useNavigate();

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
        navigate("/library/playlists");
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

const SuggestionPlaylist = React.memo(({ playlist }) => {
  const store = useAppStore();

  const playlistVideos = store.playlistVideos(playlist.id);
  const artistWeights = new Map();
  const albumWeights = new Map();
  for (const video of playlistVideos) {
    if (video.artist) {
      if (!artistWeights.has(video.artist)) {
        artistWeights.set(video.artist, 1);
      }
    }
    if (video.album) {
      if (!albumWeights.has(video.album)) {
        albumWeights.set(video.album, 1);
      }
    }
  }

  let suggestedVideos = Object.values(store.videos).filter(
    (video) => !playlist.ids.find((videoId) => videoId === video.id)
  );
  suggestedVideos = suggestedVideos
    .sort((first, second) => {
      const accumulateWeigths = (video) => {
        let weight = Math.random();
        if (artistWeights.has(video.artist)) {
          weight += artistWeights.get(video.artist);
        }
        if (albumWeights.has(video.album)) {
          weight += albumWeights.get(video.album);
        }
        return weight;
      };
      let firstWeight = accumulateWeigths(first);
      let secondWeight = accumulateWeigths(second);

      return (
        Math.random() ** (1 / (firstWeight / 3)) <
        Math.random() ** (1 / (secondWeight / 3))
      );
    })
    .slice(0, 20);

  const addToPlaylist = (video) => {
    playlist.ids.push(video.id);
    playlistAPI
      .update(playlist.id, { ids: playlist.ids })
      .catch(snackBarHandler(store));
  };

  return (
    <List sx={{ padding: "0px" }}>
      {suggestedVideos.map((video) => (
        <MediaItem
          key={video.id}
          isSmallDevice={false}
          video={video}
          isActive={video.id === store.player.videoId}
        >
          <IconButton onClick={() => addToPlaylist(video)}>
            <PlaylistAddIcon />
          </IconButton>
        </MediaItem>
      ))}
    </List>
  );
});

const Suggestions = ({ playlist }) => {
  const isFreeSpaceAvailable = useMediaQuery({
    minHeight: 2 * playlist.ids.length * 72,
  });
  const [expanded, setExpanded] = useState(isFreeSpaceAvailable);
  const [refresh, setRefresh] = useState(false);

  return (
    <>
      <Stack
        direction="row"
        alignItems="center"
        sx={{ margin: "8px 0px", cursor: "pointer" }}
        onClick={() => setExpanded(!expanded)}
      >
        <Typography variant="h6" sx={{ margin: "0px 8px" }}>
          Suggestions
        </Typography>
        <Button
          variant="outlined"
          size="small"
          onClick={(e) => {
            e.stopPropagation();
            setRefresh(!refresh);
          }}
        >
          Refresh
        </Button>
        <Box sx={{ marginLeft: "auto", color: "#606060" }}>
          {expanded ? <ExpandMoreIcon /> : <ExpandLessIcon />}
        </Box>
      </Stack>
      <Collapse
        in={expanded}
        timeout="auto"
        classes={{
          wrapper: { height: "100%" },
        }}
        sx={{
          flex: expanded ? "1 1 0" : "0 1 0",
          overflow: "auto",
          borderStyle: "solid hidden",
          borderWidth: "1px",
          borderColor: "#E0E0E0",
        }}
      >
        <SuggestionPlaylist playlist={playlist} refresh={refresh} />
      </Collapse>
    </>
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

  const playlistDuration = () => {
    let total = 0;

    for (const id of playlist.ids) {
      total += store.videos[id].duration;
    }

    return humanReadableDuration(total);
  };

  if (!playlist) {
    return null;
  }

  return (
    <Stack sx={{ flex: 1, width: "100%" }}>
      <UpdateModal
        open={isModalOpen}
        close={() => setModalOpen(false)}
        playlist={playlist}
      />
      <Box
        sx={{
          marginTop: "32px",
          marginBottom: "24px",
          marginLeft: "16px",
        }}
      >
        <Stack direction="row" alignItems="center">
          <Box sx={{ marginRight: "32px", height: 128, width: 128 }}>
            <PlaylistThumbnail videos={videos} />
          </Box>
          <Box>
            <Typography variant="h4">{playlist.name}</Typography>
            <Typography>{pluralize("media", videos.length, true)}</Typography>
            <Typography>{playlistDuration()}</Typography>
          </Box>
        </Stack>
        <Stack direction="row" sx={{ marginTop: "16px" }}>
          <Box>
            <Button
              disableElevation
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
      <Stack sx={{ flex: 1, minHeight: "0px" }}>
        <Box
          sx={{
            flex: "1.5 1 0",
            overflow: "auto",
            borderStyle: "solid hidden",
            borderWidth: "1px",
            borderColor: "#E0E0E0",
          }}
        >
          <VirtualizedMediaList
            videos={videos}
            mediaProps={{ playlist: playlist }}
          />
        </Box>
        <Suggestions playlist={playlist} />
      </Stack>
    </Stack>
  );
});

export default PlaylistPage;
