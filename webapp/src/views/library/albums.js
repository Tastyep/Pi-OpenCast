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
import PlayArrowIcon from "@mui/icons-material/PlayArrow";
import AlbumIcon from "@mui/icons-material/Album";

import { styled } from "@mui/material/styles";

import { Link } from "react-router-dom";

import { observer } from "mobx-react-lite";

import { useMediaQuery } from "react-responsive";
import { SIZES } from "constants.js";

import { queueNext, queueLast, shuffleIds } from "services/playlist";
import playlistAPI from "services/api/playlist";
import playerAPI from "services/api/player";
import snackBarHandler from "services/api/error";

import { useAppStore } from "providers/app_context";

const AlbumItemContainer = styled(ListItem)({
  flexGrow: 0,
  flowShrink: 1,
  width: "256px",
  flexDirection: "column",
  maxWidth: `calc(50% - 8px)`, // Remove the gap between items
  aspectRatio: "1/1",
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

const ThumbnailPlayButton = styled(IconButton)({
  display: "flex",
  justifyContent: "center",
  alignItems: "center",
  position: "absolute",
  bottom: "52px",
  right: "14px",
  background: "rgba(0,0,0,0.33)",
  "&:hover": {
    background: "rgba(0,0,0,0.6)",
    transform: "scale(1.3)",
  },
});

const AlbumItemThumbnail = (props) => {
  const { album, isSmallDevice, isMenuOpen, menuClick, playNext } = props;
  const [hover, setHover] = useState(isSmallDevice || isMenuOpen);

  const onMenuClick = (evt) => {
    menuClick(evt);
    evt.preventDefault();
  };

  const playAlbum = (evt) => {
    playNext(true);
    evt.preventDefault();
  };

  return (
    <Link
      to={album.id}
      onMouseEnter={() => {
        setHover(true);
      }}
      onMouseLeave={() => {
        setHover(isMenuOpen);
      }}
      style={{
        display: "flex",
        height: "100%",
        width: "100%",
        justifyContent: "center",
        alignItems: "center",
        borderRadius: "8px",
        overflow: "hidden",
        background:
          "linear-gradient(to bottom right, #C6FFDD 0%, #FBD786 50%, #F7797D 100%)",
        caretColor: "transparent",
      }}
    >
      {album.thumbnail ? (
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
      ) : (
        <AlbumIcon
          sx={{ height: "64%", width: "64%", color: "rgba(0,0,0,0.6)" }}
        />
      )}
      {hover && (
        <Stack
          justifyContent="right"
          sx={{
            height: "100%",
            width: "100%",
            position: "absolute",
            borderRadius: "8px 8px 0px 0px",
            background:
              "linear-gradient(180deg, rgba(0,0,0,0.5) 0%, rgba(0,0,0,0) 25%, rgba(0,0,0,0) 100%)",
          }}
        >
          <IconButton
            sx={{ position: "absolute", top: "8px", right: "8px" }}
            onClick={onMenuClick}
          >
            <MoreVertIcon sx={{ marginLeft: "auto", color: "#FFFFFF" }} />
          </IconButton>
          <ThumbnailPlayButton onClick={playAlbum}>
            <PlayArrowIcon sx={{ color: "#F5F5F5", marginTop: "auto" }} />
          </ThumbnailPlayButton>
        </Stack>
      )}
    </Link>
  );
};

const AlbumItem = ({ album, isSmallDevice }) => {
  const store = useAppStore();

  const [anchor, setAnchor] = useState(null);
  const isMenuOpen = Boolean(anchor);

  const closeMenu = () => {
    setAnchor(null);
  };

  const shufflePlayNext = () => {
    closeMenu();

    const shuffledIds = shuffleIds(album.ids);
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
      album.ids
    );
    playlistAPI
      .update(store.playerPlaylist.id, { ids: playlistIds })
      .then((_) => {
        if (forcePlay || store.player.isStopped) {
          playerAPI.playMedia(album.ids[0]).catch(snackBarHandler(store));
        }
      })
      .catch(snackBarHandler(store));
  };

  const queue = () => {
    closeMenu();

    const playlistIds = queueLast(
      store.playerPlaylist,
      store.player.videoId,
      album.ids
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
      <AlbumItemThumbnail
        album={album}
        isSmallDevice={isSmallDevice}
        isMenuOpen={isMenuOpen}
        menuClick={(e) => {
          setAnchor(e.currentTarget);
        }}
        playNext={playNext}
      />
      <AlbumItemBar>
        <Typography
          color="primary.contrastText"
          sx={{
            whiteSpace: "nowrap",
            overflow: "hidden",
            textOverflow: "ellipsis",
            margin: "0px 8px",
          }}
        >
          {album.name}
        </Typography>
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
      </Menu>
    </AlbumItemContainer>
  );
};

const AlbumsPage = observer(() => {
  const store = useAppStore();
  const albums = Object.values(store.albums);
  const isSmallDevice = useMediaQuery({
    maxWidth: SIZES.small.max,
  });

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
        <AlbumItem
          key={album.name}
          album={album}
          isSmallDevice={isSmallDevice}
        />
      ))}
    </List>
  );
});

export default AlbumsPage;
