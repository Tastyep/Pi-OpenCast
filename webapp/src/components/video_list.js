import {
  ImageList,
  ImageListItem,
  ImageListItemBar,
  IconButton,
} from "@mui/material";
import { styled } from '@mui/material/styles';
import { createStyles, makeStyles } from "@mui/material/styles";
import DeleteIcon from "@mui/icons-material/Delete";
import noPreview from "images/no-preview.png";
import { observer } from "mobx-react-lite";
import React from "react";
import playerAPI from "services/api/player";
import videoAPI from "services/api/video";

import { useAppStore } from "./app_context";

const PREFIX = 'VideoList';

const classes = {
  root: `${PREFIX}-root`,
  gridList: `${PREFIX}-gridList`,
  gridItem: `${PREFIX}-gridItem`,
  title: `${PREFIX}-title`,
  titleBar: `${PREFIX}-titleBar`
};

const Root = styled('div')(() =>
  ({
    [`&.${classes.root}`]: {
      display: "flex",
      flexWrap: "wrap",
      justifyContent: "center",
      overflow: "hidden",
      backgroundColor: "#F5F5F5",
    },

    [`& .${classes.gridList}`]: {
      flexWrap: "nowrap",
      // Promote the list into his own layer on Chrome. This cost memory but
      // helps keeping high FPS.
      transform: "translateZ(0)",
    },

    [`& .${classes.gridItem}`]: {
      minWidth: "160px",
    },

    [`& .${classes.title}`]: {
      color: "#F5F5F5",
    },

    [`& .${classes.titleBar}`]: {
      background:
        "linear-gradient(to top, rgba(0,0,0,0.7) 0%, rgba(0,0,0,0.3) 70%, rgba(0,0,0,0) 100%)",
    }
  }));

const VideoList = observer(({ videos }) => {

  const store = useAppStore();

  const deleteVideo = (video) => {
    videoAPI.delete_(video.id).catch((error) => console.log(error));
  };

  const playMedia = (video) => {
    playerAPI
      .playMedia(video.id, store.player.queue)
      .then((_) => {})
      .catch((error) => console.log(error));
  };

  const renderMedia = (video) => {
    return (
      <ImageListItem key={video.id} className={classes.gridItem}>
        <img
          src={video.thumbnail === null ? noPreview : video.thumbnail}
          alt={video.title}
          onClick={() => playMedia(video)}
        />
        <ImageListItemBar
          title={video.title}
          classes={{
            root: classes.titleBar,
            title: classes.title,
          }}
          actionIcon={
            <IconButton
              aria-label={`delete ${video.title}`}
              onClick={() => deleteVideo(video)}
            >
              <DeleteIcon className={classes.title} />
            </IconButton>
          }
        />
      </ImageListItem>
    );
  };

  return (
    <Root className={classes.root}>
      <ImageList className={classes.gridList} cols={6} gap={2}>
        {videos.map((video) => renderMedia(video))}
      </ImageList>
    </Root>
  );
});

export default VideoList;
