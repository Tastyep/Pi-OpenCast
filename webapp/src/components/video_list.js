import React from "react";

import { ImageList, ImageListItem, ImageListItemBar } from "@mui/material";
import Stack from "@mui/material/Stack";

import MusicVideoIcon from "@mui/icons-material/MusicVideo";

import { observer } from "mobx-react-lite";

import playerAPI from "services/api/player";
import playlistAPI from "services/api/playlist";
import snackBarHandler from "services/api/error";
import { queueNext } from "services/playlist";

import { useAppStore } from "providers/app_context";

const VideoList = observer(({ videos, count }) => {
  const store = useAppStore();

  const playMedia = (video) => {
    const playerPlaylist = store.playerPlaylist;

    if (playerPlaylist.ids.includes(video.id)) {
      playerAPI.playMedia(video.id).catch(snackBarHandler(store));
    } else {
      const ids = queueNext(playerPlaylist, store.player.videoId, [video.id]);
      playlistAPI
        .update(playerPlaylist.id, { ids: ids })
        .then(() => {
          playerAPI.playMedia(video.id).catch(snackBarHandler(store));
        })
        .catch(snackBarHandler(store));
    }
  };

  return (
    <ImageList
      cols={count}
      gap={8}
      sx={{
        flexWrap: "nowrap",
        transform: "translateZ(0)",
      }}
    >
      {[...Array(count).keys()].map((index) => {
        if (index >= videos.length) {
          return (
            <Stack
              key={index}
              direction="column"
              sx={{
                minWidth: "min(256px, 40vw)",
                aspectRatio: "1/1",
                overflow: "hidden",
              }}
            >
              <div
                style={{
                  backgroundColor: "#E3E3E3",
                  flex: 1,
                  marginBottom: "4px",
                }}
              />
              <div
                style={{
                  backgroundColor: "#E3E3E3",
                  height: "40px",
                }}
              />
            </Stack>
          );
        }

        const media = videos[index];
        return (
          <ImageListItem
            key={index}
            sx={{
              minWidth: "min(256px, 40vw)",
              aspectRatio: "1/1",
              backgroundImage: `url("${media.thumbnail}")`,
              backgroundSize: "cover",
              borderRadius: "8px",
              overflow: "hidden",
              cursor: "pointer",
            }}
            onClick={() => playMedia(media)}
          >
            {media.thumbnail ? (
              <img
                src={media.thumbnail}
                alt={media.title}
                style={{
                  width: "100%",
                  height: "100%",
                  objectFit: "cover",
                  backgroundColor: "rgba(0,0,0,0.66)",
                }}
              />
            ) : (
              <Stack
                alignItems="center"
                justifyContent="center"
                sx={{
                  width: "100%",
                  height: "100%",
                  position: "absolute",
                  background:
                    "linear-gradient(to bottom right, #C6FFDD 0%, #FBD786 50%, #F7797D 100%)",
                  caretColor: "transparent",
                }}
              >
                <MusicVideoIcon
                  sx={{ height: "50%", width: "50%", color: "rgba(0,0,0,0.6)" }}
                />
              </Stack>
            )}
            <ImageListItemBar
              title={media.title}
              sx={{ textAlign: "center" }}
            />
          </ImageListItem>
        );
      })}
    </ImageList>
  );
});

export default VideoList;
