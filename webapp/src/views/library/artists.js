import { useState } from "react";

import IconButton from "@mui/material/IconButton";
import List from "@mui/material/List";
import ListItem from "@mui/material/ListItem";
import ListItemIcon from "@mui/material/ListItemIcon";
import ListItemText from "@mui/material/ListItemText";
import Menu from "@mui/material/Menu";
import MenuItem from "@mui/material/MenuItem";
import Stack from "@mui/material/Stack";
import Typography from "@mui/material/Typography";

import ShuffleIcon from "@mui/icons-material/Shuffle";
import PlaylistPlayIcon from "@mui/icons-material/PlaylistPlay";
import QueueMusicIcon from "@mui/icons-material/QueueMusic";

import { styled } from "@mui/material/styles";

import { observer } from "mobx-react-lite";

import { useMediaQuery } from "react-responsive";
import { SIZES } from "constants.js";

import { queueNext, queueLast, shuffleIds } from "services/playlist";
import playlistAPI from "services/api/playlist";
import playerAPI from "services/api/player";
import snackBarHandler from "services/api/error";

import { useAppStore } from "components/app_context";
import { ArtistMenuThumbnail } from "components/artist_thumbnail";

const ArtistItemContainer = styled(ListItem)({
  flexGrow: 0,
  flowShrink: 1,
  width: "256px",
  flexDirection: "column",
  minWidth: "0px",
  maxWidth: `calc(50% - 8px)`, // Remove the gap between items
  aspectRatio: "1/1",
  padding: "0px 0px",
});

const ArtistItemBar = styled((props) => <Stack {...props} />)({
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

const ArtistItem = ({ artist, isSmallDevice }) => {
  const store = useAppStore();

  const [anchor, setAnchor] = useState(null);
  const isMenuOpen = Boolean(anchor);

  const closeMenu = () => {
    setAnchor(null);
  };

  const shufflePlayNext = () => {
    closeMenu();

    let videoIds = [];
    artist.videos.map((video) => videoIds.push(video.id));
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

  const playNext = (forcePlay = false) => {
    closeMenu();

    let videoIds = [];
    artist.videos.map((video) => videoIds.push(video.id));
    const playlistIds = queueNext(
      store.playerPlaylist,
      store.player.videoId,
      videoIds
    );
    playlistAPI
      .update(store.playerPlaylist.id, { ids: playlistIds })
      .then((_) => {
        if (forcePlay || store.player.isStopped) {
          playerAPI.playMedia(videoIds[0]).catch(snackBarHandler(store));
        }
      })
      .catch(snackBarHandler(store));
  };

  const queue = () => {
    closeMenu();

    let videoIds = [];
    artist.videos.map((video) => videoIds.push(video.id));
    const playlistIds = queueLast(
      store.playerPlaylist,
      store.player.videoId,
      videoIds
    );
    playlistAPI
      .update(store.playerPlaylist.id, { ids: playlistIds })
      .then((_) => {
        store.enqueueSnackbar({
          message: artist.name + " queued",
          options: {
            variant: "success",
          },
        });
      })
      .catch(snackBarHandler(store));
  };

  return (
    <ArtistItemContainer>
      <ArtistMenuThumbnail
        artist={artist}
        isSmallDevice={isSmallDevice}
        isMenuOpen={isMenuOpen}
        menuClick={(e) => {
          setAnchor(e.currentTarget);
        }}
        playNext={playNext}
      />
      <ArtistItemBar>
        <Typography
          sx={{
            color: "#FFFFFF",
            whiteSpace: "nowrap",
            overflow: "hidden",
            textOverflow: "ellipsis",
            margin: "0px 8px",
          }}
        >
          {artist.name}
        </Typography>
      </ArtistItemBar>
      <Menu
        id="artist-menu"
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
    </ArtistItemContainer>
  );
};

const ArtistsPage = observer(() => {
  const store = useAppStore();
  const artists = Object.values(store.artists());
  const isSmallDevice = useMediaQuery({
    maxWidth: SIZES.small.max,
  });

  if (artists.length === 0) {
    return null;
  }

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
      {artists.map((artist, _) => (
        <ArtistItem
          key={artist.name}
          artist={artist}
          isSmallDevice={isSmallDevice}
        />
      ))}
    </List>
  );
});

export default ArtistsPage;
