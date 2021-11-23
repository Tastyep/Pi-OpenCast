import { useState } from "react";

import { IconButton, List, Stack, Typography } from "@mui/material";
import ListItem from "@mui/material/ListItem";
import ListItemIcon from "@mui/material/ListItemIcon";
import ListItemText from "@mui/material/ListItemText";
import Menu from "@mui/material/Menu";
import MenuItem from "@mui/material/MenuItem";
import MoreVertIcon from "@mui/icons-material/MoreVert";
import ShuffleIcon from "@mui/icons-material/Shuffle";
import PlaylistPlayIcon from "@mui/icons-material/PlaylistPlay";
import QueueMusicIcon from "@mui/icons-material/QueueMusic";

import { styled } from "@mui/material/styles";

import { Link } from "react-router-dom";

import { observer } from "mobx-react-lite";

import { queueNext, queueLast, shuffleIds } from "services/playlist";
import playlistAPI from "services/api/playlist";
import playerAPI from "services/api/player";
import snackBarHandler from "services/api/error";

import { useAppStore } from "components/app_context";

const AlbumItemContainer = styled(ListItem)({
  flexGrow: 0,
  flowShrink: 1,
  width: "256px",
  flexDirection: "column",
  maxWidth: `calc(50% - 8px)`, // Remove the gap between items
  padding: "0px 0px",
});

const AlbumItemBar = styled((props) => <Stack {...props} />)({
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
  overflow: "hidden",
});

const AlbumItem = ({ album }) => {
  const store = useAppStore();

  const [anchor, setAnchor] = useState(null);
  const isMenuOpen = Boolean(anchor);

  const closeMenu = () => {
    setAnchor(null);
  };

  const shufflePlayNext = () => {
    closeMenu();

    let videoIds = [];
    album.videos.map((video) => videoIds.push(video.id));
    const playlistIds = queueNext(
      store.playerPlaylist,
      store.player.videoId,
      shuffleIds(videoIds)
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

    let videoIds = [];
    album.videos.map((video) => videoIds.push(video.id));
    const playlistIds = queueNext(
      store.playerPlaylist,
      store.player.videoId,
      videoIds
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

    let videoIds = [];
    album.videos.map((video) => videoIds.push(video.id));
    const playlistIds = queueLast(
      store.playerPlaylist,
      store.player.videoId,
      videoIds
    );
    playlistAPI
      .update(store.playerPlaylist.id, { ids: playlistIds })
      .then((_) => {
        store.enqueueSnackbar({
          message: album.name + " queued",
          options: {
            variant: "success",
          },
        });
      })
      .catch(snackBarHandler(store));
  };

  return (
    <AlbumItemContainer>
      <Link
        to={`/albums/${album.name}`}
        style={{
          display: "flex",
          height: "100%",
          width: "100%",
          borderRadius: "8px",
          overflow: "hidden",
        }}
      >
        <img
          src={album.thumbnail}
          alt={album.name}
          style={{
            height: "100%",
            width: "100%",
            objectFit: "cover",
            aspectRatio: "1/1",
          }}
        />
      </Link>
      <AlbumItemBar>
        <div
          style={{
            width: "40px",
            marginRight: "auto",
            visibility: "hidden",
          }}
        ></div>
        <Typography
          sx={{
            color: "#FFFFFF",
            whiteSpace: "nowrap",
            overflow: "hidden",
          }}
        >
          {album.name}
        </Typography>
        <IconButton
          sx={{ marginLeft: "auto" }}
          onClick={(e) => {
            setAnchor(e.currentTarget);
          }}
        >
          <MoreVertIcon sx={{ marginLeft: "auto", color: "#FFFFFF" }} />
        </IconButton>
      </AlbumItemBar>
      <Menu
        id="album-menu"
        anchorEl={anchor}
        open={isMenuOpen}
        onClose={closeMenu}
        MenuListProps={{
          "aria-labelledby": "basic-button",
        }}
        transformOrigin={{ horizontal: "right", vertical: "top" }}
        anchorOrigin={{ horizontal: "right", vertical: "bottom" }}
      >
        <MenuItem onClick={() => shufflePlayNext()}>
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
      </Menu>
    </AlbumItemContainer>
  );
};

const AlbumsPage = observer(() => {
  const store = useAppStore();
  const albums = Object.values(store.albums());

  if (albums.length === 0) {
    return null;
  }

  albums.sort((a, b) => {
    return a.name.localeCompare(b.name);
  });
  return (
    <List
      sx={{
        display: "flex",
        flexDirection: "row",
        flexWrap: "wrap",
        gap: "8px 16px",
        width: "92%",
      }}
    >
      {albums.map((album, _) => (
        <AlbumItem key={album.name} album={album} />
      ))}
    </List>
  );
});

export default AlbumsPage;
