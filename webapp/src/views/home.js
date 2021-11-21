import React, { useCallback, useState } from "react";

import { styled } from "@mui/material/styles";

import {
  Container,
  Grid,
  List,
  Divider,
  ListItem,
  ListItemText,
  ListItemAvatar,
  ListSubheader,
  LinearProgress,
  Stack,
} from "@mui/material";
import Box from "@mui/material/Box";
import Typography from "@mui/material/Typography";
import IconButton from "@mui/material/IconButton";
import ClearIcon from "@mui/icons-material/Clear";
import ShuffleIcon from "@mui/icons-material/Shuffle";

import { DragDropContext, Draggable, Droppable } from "react-beautiful-dnd";

import MediaQuery from "react-responsive";
import { SIZES } from "constants.js";

import { observer } from "mobx-react-lite";

import noPreview from "images/no-preview.png";
import playerAPI from "services/api/player";
import playlistAPI from "services/api/playlist";
import snackBarHandler from "services/api/error";
import { durationToHMS } from "services/duration";
import { queueNext, shuffleIds } from "services/playlist";

import { useAppStore } from "components/app_context";
import StreamInput from "components/stream_input";
import { MediaAvatar, PlayingMediaAvatar } from "components/media_item";

const PageContainer = styled("div")({
  display: "flex",
  flexWrap: "wrap",
  height: `calc(100% - 16px)`,
  justifyContent: "center",
  paddingTop: "16px",
  width: "100%",
});

const LargeThumbnail = styled("img")({
  width: "100%",
  height: "auto",
  maxHeight: "100%",
  objectFit: "contain",
  position: "absolute",
  top: "50%",
  left: "50%",
  transform: "translate(-50%, -50%)",
  paddingBottom: "16px",
});

const MediaItem = observer((props) => {
  const store = useAppStore();
  const { video, isActive, isLast, provided, snapshot } = props;

  const [isHover, setHover] = useState(false);

  const onMediaClicked = () => {
    if (isActive === false) {
      playerAPI.playMedia(video.id).catch(snackBarHandler(store));
      return;
    }
    playerAPI.pauseMedia().catch(snackBarHandler(store));
  };

  const downloadRatio = video.downloadRatio;
  let conditionalProps = {};
  if (isActive === true) {
    conditionalProps = {
      autoFocus: true,
      sx: { backgroundColor: "rgba(246,250,254,1)" },
    };
  }

  if (snapshot.isDragging) {
    let bgcolor = "rgba(200, 200, 200)";
    if (snapshot.draggingOver === null) {
      bgcolor = "rgba(211, 87, 87, 0.7)";
    }
    conditionalProps = {
      ...conditionalProps,
      ...{ sx: { backgroundColor: bgcolor } },
    };
  }

  return (
    <>
      <ListItem
        ref={provided.innerRef}
        {...provided.draggableProps}
        {...provided.dragHandleProps}
        button
        disableRipple
        {...conditionalProps}
        sx={{ paddingLeft: "8px" }}
        onClick={onMediaClicked}
        onMouseEnter={() => {
          setHover(true);
        }}
        onMouseLeave={() => {
          setHover(false);
        }}
      >
        <Stack direction="column" spacing={1} sx={{ width: "100%" }}>
          <Stack direction="row" alignItems="center">
            <ListItemAvatar>
              {isActive ? (
                <PlayingMediaAvatar
                  video={video}
                  isPlaying={store.player.isPlaying}
                />
              ) : (
                <MediaAvatar video={video} isHover={isHover} />
              )}
            </ListItemAvatar>
            <ListItemText primary={video.title} />
            <ListItemText
              primary={durationToHMS(video.duration)}
              sx={{
                textAlign: "right",
                minWidth: "max-content",
                marginLeft: "8px",
              }}
            />
          </Stack>
          {downloadRatio > 0 && downloadRatio < 1 && (
            <LinearProgress value={downloadRatio * 100} variant="determinate" />
          )}
        </Stack>
      </ListItem>
      {!isLast && <Divider />}
    </>
  );
});

const DraggableMediaItem = observer((props) => {
  return (
    <Draggable draggableId={props.video.id} index={props.index}>
      {(provided, snapshot) => (
        <MediaItem {...props} provided={provided} snapshot={snapshot} />
      )}
    </Draggable>
  );
});

const Playlist = observer(({ playlistId, provided }) => {
  const store = useAppStore();
  const videos = store.playlistVideos(playlistId);

  const shufflePlaylist = () => {
    const playlistIds = queueNext(
      store.playerPlaylist,
      store.player.videoId,
      shuffleIds(store.playerPlaylist.ids)
    );
    playlistAPI
      .update(store.playerPlaylist.id, { ids: playlistIds })
      .catch(snackBarHandler(store));
  };

  const emptyPlaylist = () => {
    playlistAPI
      .update(store.playerPlaylist.id, { ids: [] })
      .catch(snackBarHandler(store));
  };

  return (
    <List
      ref={provided.innerRef}
      subheader={
        <ListSubheader>
          <Stack direction="row" alignItems="center">
            <Typography sx={{ color: "#666666" }}>UP NEXT</Typography>
            <Box sx={{ marginLeft: "auto", marginRight: "-8px" }}>
              <IconButton onClick={shufflePlaylist}>
                <ShuffleIcon />
              </IconButton>
              <IconButton onClick={emptyPlaylist}>
                <ClearIcon />
              </IconButton>
            </Box>
          </Stack>
        </ListSubheader>
      }
      sx={{ width: "100%", overflow: "auto" }}
    >
      {videos.map((video, index) => (
        <DraggableMediaItem
          video={video}
          index={index}
          key={video.id}
          isActive={video.id === store.player.videoId}
          isLast={index + 1 === videos.length}
        />
      ))}
      {provided.placeholder}
    </List>
  );
});

const DroppablePlaylist = ({ playlistId }) => {
  const store = useAppStore();

  const onDragEnd = useCallback(
    (result) => {
      const { destination, source, draggableId } = result;

      if (!destination) {
        const playlist = store.playlists[source.droppableId];
        store.removePlaylistVideo(playlist.id, draggableId);
        playlistAPI
          .update(playlist.id, { ids: playlist.ids })
          .catch(snackBarHandler(store));
        return;
      }

      if (
        destination.droppableId === source.droppableId &&
        destination.index === source.index
      ) {
        return;
      }

      store.removePlaylistVideo(source.droppableId, draggableId);
      store.insertPlaylistVideo(
        destination.droppableId,
        draggableId,
        destination.index
      );

      const destPlaylist = store.playlists[destination.droppableId];
      playlistAPI
        .update(destination.droppableId, { ids: destPlaylist.ids })
        .catch(snackBarHandler(store));
    },
    [store]
  );

  if (!playlistId) {
    return null;
  }

  return (
    <DragDropContext onDragEnd={onDragEnd}>
      <Droppable droppableId={playlistId}>
        {(provided, _) => (
          <Playlist playlistId={playlistId} provided={provided} />
        )}
      </Droppable>
    </DragDropContext>
  );
};

const PlayingMediaThumbnail = observer(() => {
  const store = useAppStore();
  const video = store.videos[store.player.videoId];

  if (!video) {
    return null;
  }

  return (
    <LargeThumbnail
      src={video.thumbnail === null ? noPreview : video.thumbnail}
      alt={video.title}
    />
  );
});

const HomePage = observer(() => {
  const store = useAppStore();
  const playlistId = store.player.queue;

  if (!playlistId) {
    return null;
  }

  return (
    <PageContainer>
      <MediaQuery minWidth={SIZES.large.min}>
        {(matches) =>
          matches ? (
            <Grid container justifyContent="center" sx={{ height: "100%" }}>
              <Grid item xs={8} sx={{ height: "100%" }}>
                <Container sx={{ height: "100%" }}>
                  <Stack direction="column" sx={{ height: "100%" }}>
                    <div
                      style={{
                        width: "100%",
                        marginBottom: "16px",
                      }}
                    >
                      <StreamInput />
                    </div>
                    <div style={{ position: "relative", height: "100%" }}>
                      <PlayingMediaThumbnail />
                    </div>
                  </Stack>
                </Container>
              </Grid>
              <Grid item xs={4} sx={{ height: "100%" }}>
                <Stack direction="row" sx={{ height: "100%" }}>
                  <Divider
                    orientation="vertical"
                    sx={{
                      backgroundColor: "#F0F0F0",
                    }}
                  />
                  <DroppablePlaylist playlistId={playlistId} />
                </Stack>
              </Grid>
            </Grid>
          ) : (
            <Stack sx={{ height: "100%", width: "100%" }}>
              <div
                style={{
                  width: "100%",
                  paddingLeft: "16px",
                  paddingRight: "16px",
                  marginBottom: "16px",
                  boxSizing: "border-box",
                }}
              >
                <StreamInput />
              </div>
              <DroppablePlaylist playlistId={playlistId} />
            </Stack>
          )
        }
      </MediaQuery>
    </PageContainer>
  );
});

export default HomePage;
