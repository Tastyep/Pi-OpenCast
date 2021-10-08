import {
  ImageList,
  ImageListItem,
  ImageListItemBar,
  IconButton,
} from "@material-ui/core";
import { createStyles, makeStyles } from "@material-ui/core/styles";
import DeleteIcon from "@material-ui/icons/Delete";
import noPreview from "images/no-preview.png";
import { observer } from "mobx-react-lite";
import React from "react";
import playerAPI from "services/api/player";
import videoAPI from "services/api/video";

import { useAppStore } from "./app_context";

const useStyles = makeStyles(() =>
  createStyles({
    root: {
      display: "flex",
      flexWrap: "wrap",
      justifyContent: "center",
      overflow: "hidden",
      backgroundColor: "#F5F5F5",
    },
    gridList: {
      flexWrap: "nowrap",
      // Promote the list into his own layer on Chrome. This cost memory but
      // helps keeping high FPS.
      transform: "translateZ(0)",
    },
    gridItem: {
      minWidth: "160px",
    },
    title: {
      color: "#F5F5F5",
    },
    titleBar: {
      background:
        "linear-gradient(to top, rgba(0,0,0,0.7) 0%, rgba(0,0,0,0.3) 70%, rgba(0,0,0,0) 100%)",
    },
  })
);

const VideoList = observer(({ videos }) => {
  const classes = useStyles();
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
    <div className={classes.root}>
      <ImageList className={classes.gridList} cols={6} gap={2}>
        {videos.map((video) => renderMedia(video))}
      </ImageList>
    </div>
  );
});

export default VideoList;
