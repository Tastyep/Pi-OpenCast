import React from "react";

import { ImageList, ImageListItem, ImageListItemBar } from "@mui/material";
import Stack from "@mui/material/Stack";

import noPreview from "images/no-preview.png";

import { observer } from "mobx-react-lite";

import playerAPI from "services/api/player";
import playlistAPI from "services/api/playlist";
import snackBarHandler from "services/api/error";
import { queueNext } from "services/playlist";

import { useAppStore } from "./app_context";

const VideoList = observer(({ videos }) => {
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

  const MediaItem = ({ media }) => {
    if (media === null) {
      return (
        <Stack
          direction="column"
          sx={{
            minWidth: "200px",
            aspectRatio: "16/9",
            overflow: "hidden",
          }}
        >
          <div
            style={{ backgroundColor: "#E3E3E3", flex: 1, marginBottom: "4px" }}
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

    return (
      <ImageListItem
        sx={{
          minWidth: "200px",
          aspectRatio: "16/9",
          backgroundImage: `url("${media.thumbnail}")`,
          backgroundSize: "cover",
        }}
      >
        <img
          src={media.thumbnail === null ? noPreview : media.thumbnail}
          alt={media.title}
          style={{
            width: "100%",
            height: "100%",
            objectFit: "contain",
            backgroundColor: "rgba(0,0,0,0.66)",
          }}
          onClick={() => playMedia(media)}
        />
        <ImageListItemBar title={media.title} sx={{ textAlign: "center" }} />
      </ImageListItem>
    );
  };

  return (
    <ImageList
      cols={6}
      gap={2}
      sx={{ flexWrap: "nowrap", transform: "translateZ(0)" }}
    >
      {[...Array(6).keys()].map((index) => (
        <MediaItem
          key={index}
          media={index < videos.length ? videos[index] : null}
        />
      ))}
    </ImageList>
  );
});

export default VideoList;
