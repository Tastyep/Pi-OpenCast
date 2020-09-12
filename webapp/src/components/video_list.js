import React, { useState, useEffect } from "react";

import { Theme, createStyles, makeStyles } from "@material-ui/core/styles";
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

const useStyles = makeStyles((theme: Theme) =>
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

function VideoList() {
  const classes = useStyles();
  const [videos, setVideos] = useState([]);
  const [timer, setTimer] = useState(0);
  const [videoId, setVideoId] = useState(null);

  const deleteVideo = (video) => {
    videoAPI
      .delete_(video.id)
      .then((response) => {
        listVideos();
      })
      .catch((error) => console.log(error));
  };

  const playMedia = (video) => {
    playerAPI
      .playMedia(video.id)
      .then((response) => {
        setVideoId(video.id);
      })
      .catch((error) => console.log(error));
  };

  const listVideos = () => {
    videoAPI
      .list()
      .then((response) => {
        setVideos(response.data);
      })
      .catch((error) => console.log(error));
  };

  useEffect(() => {
    let interval;
    interval = setInterval(() => setTimer(timer + 1), 10000);

    listVideos();

    return () => clearInterval(interval);
  }, [timer]);

  return (
    <div className={classes.root}>
      <GridList className={classes.gridList} cols={4} spacing={2}>
        {videos.map((tile) => (
          <GridListTile key={tile.thumbnail}>
            <img
              src={tile.thumbnail === null ? noPreview : tile.thumbnail}
              alt={tile.title}
              onClick={() => playMedia(tile)}
            />
            <GridListTileBar
              title={tile.title}
              classes={{
                root: classes.titleBar,
                title: classes.title,
              }}
              actionIcon={
                <IconButton
                  aria-label={`delete ${tile.title}`}
                  onClick={() => deleteVideo(tile)}
                >
                  <DeleteIcon className={classes.title} />
                </IconButton>
              }
            />
            )}
          </GridListTile>
        ))}
      </GridList>
    </div>
  );
}

export default VideoList;
