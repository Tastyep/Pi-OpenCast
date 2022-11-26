import React, { useCallback, useEffect, useRef, useState } from "react";

import { styled, useTheme } from "@mui/material/styles";

import {
  Grid,
  Divider,
  ListItemText,
  ListItemAvatar,
  LinearProgress,
  Stack,
  Button,
} from "@mui/material";
import Box from "@mui/material/Box";
import IconButton from "@mui/material/IconButton";
import InputAdornment from "@mui/material/InputAdornment";
import List from "@mui/material/List";
import ListItemButton from "@mui/material/ListItemButton";
import ShuffleIcon from "@mui/icons-material/Shuffle";
import TextField from "@mui/material/TextField";
import Paper from "@mui/material/Paper";

import SearchIcon from "@mui/icons-material/Search";
import DeleteIcon from "@mui/icons-material/Delete";
import ClearIcon from "@mui/icons-material/Clear";

import { DragDropContext, Draggable, Droppable } from "react-beautiful-dnd";
import { Virtuoso } from "react-virtuoso";

import { useMediaQuery } from "react-responsive";
import { SIZES } from "constants.js";

import { observer } from "mobx-react-lite";

import MediaControl from "views/media_control";

import { MediaAvatar, PlayingMediaAvatar } from "components/media_item";

import playerAPI from "services/api/player";
import playlistAPI from "services/api/playlist";
import snackBarHandler from "services/api/error";
import { durationToHMS } from "services/duration";
import { filterVideos, queueNext, shuffleIds } from "services/playlist";

import { useAppStore } from "providers/app_context";

const PageContainer = styled("div", {
  shouldForwardProp: (props) => props !== "smallSize",
})(({ smallSize }) => ({
  display: "flex",
  flex: 1,
  flexWrap: "wrap",
  justifyContent: "center",
  paddingTop: smallSize ? "12px" : "24px",
  paddingBottom: smallSize ? "0px" : "24px",
  width: "100%",
}));

const MediaItem = observer((props) => {
  const store = useAppStore();
  const { video, isActive, provided, isDragging, draggingOver } = props;

  const [isHover, setHover] = useState(false);

  const onMediaClicked = () => {
    if (isActive === false) {
      playerAPI.playMedia(video.id).catch(snackBarHandler(store));
      return;
    }
    playerAPI.pauseMedia().catch(snackBarHandler(store));
  };

  const downloadRatio = video.downloadRatio;

  let styles = {};
  const theme = useTheme();
  if (isDragging) {
    styles["backgroundColor"] =
      draggingOver === null
        ? theme.palette.error.main
        : theme.palette.action.hover;
  }

  return (
    <>
      <ListItemButton
        ref={provided.innerRef}
        {...provided.draggableProps}
        {...provided.dragHandleProps}
        disableRipple
        selected={isActive}
        sx={styles}
        onClick={onMediaClicked}
        onMouseEnter={() => {
          setHover(true);
        }}
        onMouseLeave={() => {
          setHover(false);
        }}
      >
        <Stack
          direction="column"
          spacing={1}
          justifyContent="center"
          sx={{ width: "100%", height: "64px" }}
        >
          <Stack
            direction="row"
            alignItems="center"
            sx={{ flex: 1, height: "100%" }}
          >
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
            <ListItemText
              primary={video.title}
              sx={{ maxHeight: "100%", overflow: "hidden" }}
            />
            <ListItemText
              primary={durationToHMS(video.duration * 1000)}
              sx={{
                textAlign: "right",
                minWidth: "max-content",
                marginLeft: "8px",
              }}
            />
          </Stack>
          {downloadRatio > 0 && downloadRatio < 1 && (
            <LinearProgress
              value={downloadRatio * 100}
              variant="determinate"
              sx={{ minHeight: "4px" }}
            />
          )}
        </Stack>
      </ListItemButton>
    </>
  );
});

const DraggableMediaItem = observer((props) => {
  const { video, index } = props;

  return (
    <Draggable draggableId={video.id} index={index}>
      {(provided, _) => (
        <MediaItem
          {...props}
          provided={provided}
          isDragging={false}
          draggingOver={null}
        />
      )}
    </Draggable>
  );
});

const Playlist = observer(({ virtuoso, videos, provided }) => {
  const store = useAppStore();
  const activeVideoId = store.player.videoId;

  const itemContent = (index, video) => (
    <DraggableMediaItem
      video={video}
      index={index}
      key={video.id}
      isActive={video.id === activeVideoId}
    />
  );

  const Components = React.useMemo(() => {
    return {
      HeightPreservingItem: ({ children, ...props }) => {
        return (
          // the height is necessary to prevent the item container from collapsing, which confuses Virtuoso measurements
          <List
            {...props}
            sx={{
              height: props["data-known-size"] || undefined,
              padding: "0px",
            }}
          >
            {children}
          </List>
        );
      },
    };
  }, []);

  let activeVideoIndex = 0;
  for (; activeVideoIndex < videos.length; activeVideoIndex++) {
    if (videos[activeVideoIndex].id === activeVideoId) {
      break;
    }
  }

  if (activeVideoIndex === videos.length) {
    activeVideoIndex = 0;
  }

  return (
    <Virtuoso
      data={videos}
      ref={virtuoso}
      scrollerRef={provided.innerRef}
      initialTopMostItemIndex={activeVideoIndex}
      itemContent={itemContent}
      components={{ Item: Components.HeightPreservingItem }}
    />
  );
});

const DroppablePlaylist = observer(({ playlistId }) => {
  const store = useAppStore();

  const [input, setInput] = useState("");
  const virtuoso = useRef(null);

  const onDragEnd = useCallback(
    (result, videos) => {
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

      const playlist = store.playlists[destination.droppableId];
      const nextVideo = videos[destination.index];
      const realIndex = playlist.ids.indexOf(nextVideo.id);

      store.removePlaylistVideo(source.droppableId, draggableId);
      store.insertPlaylistVideo(playlist.id, draggableId, realIndex);

      const destPlaylist = store.playlists[destination.droppableId];
      playlistAPI
        .update(destination.droppableId, { ids: destPlaylist.ids })
        .catch(snackBarHandler(store));
    },
    [store]
  );
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

  const updateInputContent = (e) => {
    setInput(e.target.value);
  };

  const updateBlur = (evt) => {
    if (evt.key === "Enter") {
      evt.target.blur();
    }
  };

  const videos = filterVideos(
    store.artists,
    store.albums,
    store.playlistVideos(playlistId),
    input
  );

  const scrollToActiveVideo = () => {
    let videoIdx = videos.findIndex(
      (video) => video.id == store.player.videoId
    );
    if (videoIdx === -1) {
      videoIdx = 0;
    }

    virtuoso.current.scrollToIndex({
      index: videoIdx,
      align: "start",
      behavior: "auto",
    });
  };

  if (!playlistId) {
    return null;
  }

  const endAdornment =
    input.length > 0 ? (
      <InputAdornment position="end">
        <IconButton color="primary" onClick={() => setInput("")}>
          <ClearIcon />
        </IconButton>
      </InputAdornment>
    ) : (
      <InputAdornment position="end">
        <IconButton color="primary">
          <SearchIcon />
        </IconButton>
      </InputAdornment>
    );

  return (
    <Stack direction="column" sx={{ width: "100%", height: "100%" }}>
      <Stack
        direction="row"
        alignItems="center"
        sx={{ margin: "0px 0px 8px 0px" }}
      >
        <Button
          variant="outlined"
          color="primary"
          sx={{
            whiteSpace: "nowrap",
            margin: "0px 8px",
            justifyContent: "center",
            alignItems: "center",
            // color: theme.palette.secondary.dark,
          }}
          onClick={scrollToActiveVideo}
        >
          UP NEXT
        </Button>
        <Stack direction="row" justifyContent="end" sx={{ flex: "3" }}>
          <TextField
            fullWidth
            variant="standard"
            label="Filter"
            size="small"
            value={input}
            onChange={updateInputContent}
            onKeyPress={updateBlur}
            InputProps={{
              endAdornment: endAdornment,
            }}
            sx={{
              flex: "1",
              transform: "translateY(-8px)",
              maxWidth: "200px",
              margin: "0px 8px",
            }}
          />
          <IconButton
            color="secondary"
            sx={{ flex: 0 }}
            onClick={shufflePlaylist}
          >
            <ShuffleIcon />
          </IconButton>
          <IconButton
            color="secondary"
            sx={{ flex: 0 }}
            onClick={emptyPlaylist}
          >
            <DeleteIcon />
          </IconButton>
        </Stack>
      </Stack>
      <Divider sx={{ height: "2px" }} />
      <Box sx={{ flex: 1 }}>
        {videos.length === 0 ? null : (
          <DragDropContext onDragEnd={(result) => onDragEnd(result, videos)}>
            <Droppable
              droppableId={playlistId}
              mode="virtual"
              renderClone={(provided, snapshot, rubric) => {
                const video = videos[rubric.source.index];
                return (
                  <MediaItem
                    video={video}
                    provided={provided}
                    isDragging={snapshot.isDragging}
                    draggingOver={snapshot.draggingOver}
                    isActive={video.id === store.player.videoId}
                    isLast={rubric.source.index + 1 === videos.length}
                  />
                );
              }}
              style={{ width: "100%" }}
            >
              {(provided) => (
                <Playlist
                  virtuoso={virtuoso}
                  videos={videos}
                  provided={provided}
                />
              )}
            </Droppable>
          </DragDropContext>
        )}
      </Box>
    </Stack>
  );
});

const HomePage = observer(() => {
  const store = useAppStore();
  const playlistId = store.player.queue;

  useEffect(() => {
    if (playlistId) {
      store.loadPlaylistVideos(playlistId);
    }
  }, [store, playlistId]);

  const mediumSize = useMediaQuery({
    maxWidth: SIZES.medium.max,
  });

  if (!playlistId) {
    return null;
  }

  return (
    <PageContainer smallSize={mediumSize}>
      {mediumSize ? (
        <Stack sx={{ height: "100%", width: "100%" }}>
          <DroppablePlaylist playlistId={playlistId} />
        </Stack>
      ) : (
        <Grid container justifyContent="center" sx={{ height: "100%" }}>
          <Grid
            container
            item
            alignItems="center"
            justifyContent="center"
            xs={8}
            sx={{ paddingRight: "24px" }}
          >
            <MediaControl iconColor="primary" />
          </Grid>
          <Grid
            item
            container
            xs={4}
            justifyContent="flex-end"
            sx={{ height: "100%" }}
          >
            <Paper
              elevation={2}
              sx={{
                display: "flex",
                flex: 1,
                padding: "12px 12px 12px 12px",
              }}
            >
              <DroppablePlaylist playlistId={playlistId} />
            </Paper>
          </Grid>
        </Grid>
      )}
    </PageContainer>
  );
});

export default HomePage;
