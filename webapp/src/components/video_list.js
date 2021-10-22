import React from "react";

import { ImageList, ImageListItem, ImageListItemBar } from "@mui/material";
import Stack from "@mui/material/Stack";
import { styled } from "@mui/material/styles";

import noPreview from "images/no-preview.png";

import { observer } from "mobx-react-lite";

import playerAPI from "services/api/player";
import snackBarHandler from "services/api/error";

import { useAppStore } from "./app_context";

const ImageListContainer = styled("div")({
  display: "flex",
  flexWrap: "wrap",
  justifyContent: "center",
  overflow: "hidden",
});

const VideoList = observer(({ videos }) => {
  const store = useAppStore();

  const playMedia = (video) => {
    playerAPI
      .playMedia(video.id, store.player.queue)
      .then((_) => {})
      .catch(snackBarHandler(store));
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
        <>
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
        </>
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
