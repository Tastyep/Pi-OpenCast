import React, { useState } from "react";

import { Divider, Grid, Tabs, Tab, Typography } from "@mui/material";
import { styled } from "@mui/material/styles";

import { Switch, Route, Link, useRouteMatch } from "react-router-dom";

import { observer } from "mobx-react-lite";

import AlbumsPage from "views/library/albums";
import ArtistsPage from "views/library/artists";
import MediasPage from "views/library/medias";
import PlaylistsPage from "views/library/playlists";

import { useAppStore } from "components/app_context";
import VideoList from "components/video_list";

const PREFIX = "LibraryPage";

const classes = {
  subPageContainer: `${PREFIX}-subPageContainer`,
  listTitle: `${PREFIX}-listTitle`,
  listDivider: `${PREFIX}-listDivider`,
};

// TODO jss-to-styled codemod: The Fragment root was replaced by div. Change the tag if needed.
const Root = styled("div")(() => ({
  [`& .${classes.subPageContainer}`]: {
    height: `calc(100% - 50px)`,
    overflow: "auto",
  },

  [`& .${classes.listTitle}`]: {
    marginTop: "40px",
    marginBottom: "20px",
  },

  [`& .${classes.listDivider}`]: {
    marginTop: "40px",
    marginBottom: "20px",
  },
}));

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

  let { path, url } = useRouteMatch();
  const [value, setValue] = useState(0);

  return (
    <Root>
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
    </Root>
  );
});

export default LibraryPage;
