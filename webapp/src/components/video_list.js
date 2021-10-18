import React from "react";

import { ImageList, ImageListItem, ImageListItemBar } from "@mui/material";
import { styled } from "@mui/material/styles";

import noPreview from "images/no-preview.png";

import { observer } from "mobx-react-lite";

import playerAPI from "services/api/player";

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
      .catch((error) => console.log(error));
  };

  const renderMedia = (video) => {
    return (
      <ImageListItem
        key={video.id}
        sx={{
          minWidth: "160px",
          aspectRatio: "16/9",
          backgroundImage: `url("${video.thumbnail}")`,
          backgroundSize: "cover",
        }}
      >
        <div
          style={{
            height: "100%",
            width: "100%",
            backgroundColor: "rgba(0,0,0,0.66)",
          }}
        >
          <img
            src={video.thumbnail === null ? noPreview : video.thumbnail}
            alt={video.title}
            style={{ width: "100%", height: "100%", objectFit: "contain" }}
            onClick={() => playMedia(video)}
          />
        </div>
        <ImageListItemBar title={video.title} sx={{ textAlign: "center" }} />
      </ImageListItem>
    );
  };

  return (
    <ImageListContainer>
      <ImageList
        cols={6}
        gap={2}
        sx={{ flexWrap: "nowrap", transform: "translateZ(0)" }}
      >
        {videos.map((video) => renderMedia(video))}
      </ImageList>
    </ImageListContainer>
  );
});

export default VideoList;
