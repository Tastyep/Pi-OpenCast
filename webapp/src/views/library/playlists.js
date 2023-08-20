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
import DeleteIcon from "@mui/icons-material/Delete";
import PlaylistPlayIcon from "@mui/icons-material/PlaylistPlay";
import QueueMusicIcon from "@mui/icons-material/QueueMusic";
import ShuffleIcon from "@mui/icons-material/Shuffle";

import { styled } from "@mui/material/styles";

import { Link } from "react-router-dom";

import { observer } from "mobx-react-lite";

import { useMediaQuery } from "react-responsive";
import { useActiveSize } from "services/size";
import { SIZES, MARGINS } from "constants.js";

import { queueNext, queueLast, shuffleIds } from "services/playlist";
import playlistAPI from "services/api/playlist";
import playerAPI from "services/api/player";
import snackBarHandler from "services/api/error";

import { useAppStore } from "providers/app_context";
import { PlaylistMenuThumbnail } from "components/playlist_thumbnail";
import PlaylistModal from "components/playlist_modal";

const PlaylistItemContainer = styled(ListItem)(({ width }) => ({
  flexGrow: 0,
  flowShrink: 1,
  width: width,
  flexDirection: "column",
  maxWidth: `calc(50% - 8px)`, // Remove the gap between items
  aspectRatio: "1/1",
  padding: "0px", // prevent items be less than the parent size
}));

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

const PlaylistItem = ({ playlist, size }) => {
  const store = useAppStore();

  const [anchor, setAnchor] = useState(null);
  const isMenuOpen = Boolean(anchor);

  const closeMenu = () => {
    setAnchor(null);
  };

  const shufflePlayNext = () => {
    closeMenu();

    const shuffledIds = shuffleIds(playlist.ids);
    const playlistIds = queueNext(
      store.playerPlaylist,
      store.player.videoId,
      shuffledIds
    );
    playlistAPI
      .update(store.playerPlaylist.id, { ids: playlistIds })
      .then((_) => {
        if (store.player.videoId !== shuffledIds[0]) {
          playerAPI.playMedia(shuffledIds[0]).catch(snackBarHandler(store));
        }
      })
      .catch(snackBarHandler(store));
  };

  const playNext = (forcePlay = false) => {
    closeMenu();
    const playlistIds = queueNext(
      store.playerPlaylist,
      store.player.videoId,
      playlist.ids
    );
    playlistAPI
      .update(store.playerPlaylist.id, { ids: playlistIds })
      .then((_) => {
        if (forcePlay || store.player.isStopped) {
          playerAPI.playMedia(playlist.ids[0]).catch(snackBarHandler(store));
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

  const removePlaylist = () => {
    closeMenu();
    playlistAPI.delete_(playlist.id).catch(snackBarHandler(store));
  };

  return (
    <PlaylistItemContainer
      width={size.compareTo(SIZES.large) < 0 ? "256px" : "448px"}
    >
      <Link
        to={playlist.id}
        style={{
          width: "100%",
          aspectRatio: "1/1",
          borderRadius: "8px",
          overflow: "hidden",
          background:
            "linear-gradient(to bottom right, #C6FFDD 0%, #FBD786 50%, #F7797D 100%)",
        }}
      >
        <PlaylistMenuThumbnail
          videos={store.playlistVideos(playlist.id)}
          isSmallDevice={size.compareTo(SIZES.small) <= 0}
          isMenuOpen={isMenuOpen}
          menuClick={(e) => {
            setAnchor(e.currentTarget);
          }}
          playNext={playNext}
        />
      </Link>
      <PlaylistItemBar>
        <Typography
          sx={{ color: "#FFFFFF", whiteSpace: "nowrap", overflow: "hidden" }}
        >
          {playlist.name}
        </Typography>
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
            <ShuffleIcon color="primary" />
          </ListItemIcon>
          <ListItemText>Shuffle play</ListItemText>
        </MenuItem>
        <MenuItem onClick={() => playNext()}>
          <ListItemIcon>
            <PlaylistPlayIcon color="primary" />
          </ListItemIcon>
          <ListItemText>Play next</ListItemText>
        </MenuItem>
        <MenuItem onClick={() => queue()}>
          <ListItemIcon>
            <QueueMusicIcon color="primary" />
          </ListItemIcon>
          <ListItemText>Add to queue</ListItemText>
        </MenuItem>
        <MenuItem onClick={removePlaylist}>
          <ListItemIcon>
            <DeleteIcon color="primary" />
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
  const sizeKey = useActiveSize();
  const size = SIZES[sizeKey];
  if (!size) {
    return null;
  }
  console.log(size);
  const margin = MARGINS[sizeKey];

  playlists.sort((a, b) => {
    return a.name.localeCompare(b.name);
  });
  return (
    <Stack direction="column" sx={{ flex: 1, caretColor: "transparent" }}>
      <PlaylistModal open={open} close={() => setOpen(false)} />
      <List
        sx={{
          display: "flex",
          flexDirection: "row",
          flexWrap: "wrap",
          gap: margin.margin,
          alignContent: "baseline",
          overflow: "auto",
        }}
      >
        <PlaylistItemContainer
          width={size.compareTo(SIZES.large) < 0 ? "256px" : "448px"}
        >
          <IconButton
            sx={{
              width: "100%",
              height: "100%",
              backgroundColor: "#F0F0F0",
              borderRadius: "8px",
            }}
            onClick={() => setOpen(true)}
          >
            <AddIcon color="primary" sx={{ height: "25%", width: "25%" }} />
          </IconButton>
          <PlaylistItemBar>
            <Typography sx={{ color: "#FFFFFF" }}>New playlist</Typography>
          </PlaylistItemBar>
        </PlaylistItemContainer>
        {playlists.map((playlist, _) => (
          <PlaylistItem key={playlist.id} playlist={playlist} size={size} />
        ))}
      </List>
    </Stack>
  );
});

export default PlaylistsPage;
