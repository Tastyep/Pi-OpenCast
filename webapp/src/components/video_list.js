import React from "react";

import { createStyles, makeStyles } from "@material-ui/core/styles";
import {
  GridList,
  GridListTile,
  GridListTileBar,
  IconButton,
} from "@material-ui/core";
import DeleteIcon from "@material-ui/icons/Delete";

import videoAPI from "services/api/video";
import playerAPI from "services/api/player";

import noPreview from "images/no-preview.png";

import "./stream_input.css";
import { useAppStore } from "./app_context";
import { observer } from "mobx-react-lite";

const useStyles = makeStyles((theme) =>
  createStyles({
    root: {
      display: "flex",
      flexWrap: "wrap",
      justifyContent: "center",
      overflow: "hidden",
      backgroundColor: theme.palette.background.paper,
    },
    gridList: {
      flexWrap: "nowrap",
      // Promote the list into his own layer on Chrome. This cost memory but helps keeping high FPS.
      transform: "translateZ(0)",
    },
    title: {
      color: theme.palette.primary.light,
    },
    titleBar: {
      background:
        "linear-gradient(to top, rgba(0,0,0,0.7) 0%, rgba(0,0,0,0.3) 70%, rgba(0,0,0,0) 100%)",
    },
  })
);

const VideoList = observer(() => {
  const classes = useStyles();
  const store = useAppStore();
  const videos = store.playlistVideos(store.player.queue);

  const deleteVideo = (video) => {
    videoAPI.delete_(video.id).catch((error) => console.log(error));
  };

  const playMedia = (video) => {
    playerAPI
      .playMedia(video.id)
      .then((_) => {})
      .catch((error) => console.log(error));
  };

  return (
    <div className={classes.root}>
      <GridList className={classes.gridList} cols={4} spacing={2}>
        {videos.map((video) => (
          <GridListTile key={video.thumbnail}>
            <img
              src={video.thumbnail === null ? noPreview : video.thumbnail}
              alt={video.title}
              onClick={() => playMedia(video)}
            />
            <GridListTileBar
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
          </GridListTile>
        ))}
      </GridList>
    </div>
  );
});

export default VideoList;
