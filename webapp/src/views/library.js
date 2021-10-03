import React, { useState } from "react";

import { observer } from "mobx-react-lite";

import { Divider, Grid, Tabs, Tab, Typography } from "@material-ui/core";

import { Switch, Route, Link, useRouteMatch } from "react-router-dom";

import AlbumsPage from "views/library/albums";
import ArtistsPage from "views/library/artists";
import MediasPage from "views/library/medias";
import PlaylistsPage from "views/library/playlists";

import { useAppStore } from "components/app_context";
import VideoList from "components/video_list";

const LibraryPage = observer(() => {
  const store = useAppStore();
  let { path, url } = useRouteMatch();
  const [value, setValue] = useState(0);

  const listLastPlayedVideos = () => {
    const videos = Object.values(store.videos)
      .sort((a, b) => {
        return new Date(a.last_play) < new Date(b.last_play);
      })
      .slice(0, 5);
    console.log("IT", videos);
    return videos;
  };

  const listPopularVideos = () => {
    const videos = Object.values(store.videos)
      .sort((a, b) => {
        return a.total_playing_duration < b.total_playing_duration;
      })
      .slice(0, 5);
    console.log("IT", videos);
    return videos;
  };

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
      <Switch>
        <Route exact path={path}>
          <Typography variant="h6">Recent activity</Typography>
          <VideoList videos={listLastPlayedVideos()} />
          <Divider />
          <Typography variant="h6">Most played</Typography>
          <VideoList videos={listPopularVideos()} />
          <Divider />
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
    </>
  );
});

export default LibraryPage;
