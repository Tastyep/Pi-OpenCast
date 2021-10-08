import React, { useState } from "react";

import { observer } from "mobx-react-lite";

import { Divider, Grid, Tabs, Tab, Typography } from "@material-ui/core";
import { makeStyles, createStyles } from "@material-ui/core/styles";

import { Switch, Route, Link, useRouteMatch } from "react-router-dom";

import AlbumsPage from "views/library/albums";
import ArtistsPage from "views/library/artists";
import MediasPage from "views/library/medias";
import PlaylistsPage from "views/library/playlists";

import { useAppStore } from "components/app_context";
import VideoList from "components/video_list";

const useStyles = makeStyles(() =>
  createStyles({
    subPageContainer: {
      height: `calc(100% - 50px)`,
      overflow: "auto",
    },
    listTitle: {
      marginTop: "40px",
      marginBottom: "20px",
    },
    listDivider: {
      marginTop: "40px",
      marginBottom: "20px",
    },
  })
);

const listLastPlayedVideos = (storeVideos) => {
  const videos = Object.values(storeVideos)
    .sort((a, b) => {
      return new Date(a.last_play) < new Date(b.last_play);
    })
    .slice(0, 6);
  return videos;
};

const listPopularVideos = (storeVideos) => {
  const videos = Object.values(storeVideos)
    .sort((a, b) => {
      return a.total_playing_duration < b.total_playing_duration;
    })
    .slice(0, 6);
  return videos;
};

const LibraryPage = observer(() => {
  const store = useAppStore();
  const classes = useStyles();
  let { path, url } = useRouteMatch();
  const [value, setValue] = useState(0);

  return (
    <>
      <Tabs
        value={value}
        onChange={(_, newValue) => {
          setValue(newValue);
        }}
      >
        <Tab label="Overview" to={`${url}`} component={Link} />
        <Tab label="Playlists" to={`${url}/playlists`} component={Link} />
        <Tab label="Artists" to={`${url}/artists`} component={Link} />
        <Tab label="Albums" to={`${url}/albums`} component={Link} />
        <Tab label="Titles" to={`${url}/medias`} component={Link} />
      </Tabs>
      <Divider />
      <div className={classes.subPageContainer}>
        <Switch>
          <Route exact path={path}>
            <Typography variant="h6" className={classes.listTitle}>
              Recent activity
            </Typography>
            <VideoList videos={listLastPlayedVideos(store.videos)} />
            <Divider className={classes.listDivider} />
            <Typography variant="h6" className={classes.listTitle}>
              Most played
            </Typography>
            <VideoList videos={listPopularVideos(store.videos)} />
            <Divider className={classes.listDivider} />{" "}
          </Route>
          <Route path={`${path}/playlists`}>
            <PlaylistsPage />
          </Route>
          <Route path={`${path}/artists`}>
            <ArtistsPage />
          </Route>
          <Route path={`${path}/albums`}>
            <AlbumsPage />
          </Route>
          <Route path={`${path}/medias`}>
            <MediasPage />
          </Route>
        </Switch>
      </div>
    </>
  );
});

export default LibraryPage;
