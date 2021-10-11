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

const PageContainer = styled("div")({
  height: "100%",
  width: "92%",
  margin: "auto",
  overflow: "auto",
});

const SubPageContainer = styled("div")({
  height: `calc(100% - 50px)`,
  overflow: "auto",
});

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
    <PageContainer>
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
      <SubPageContainer>
        <Switch>
          <Route exact path={path}>
            <Typography variant="h6" sx={{ paddingTop: "32px" }}>
              Recent activity
            </Typography>
            <VideoList videos={listLastPlayedVideos(store.videos)} />
            <Divider
              sx={{
                margin: "32px 0px",
              }}
            />
            <Typography variant="h6" sx={{ paddingTop: "16px" }}>
              Most played
            </Typography>
            <VideoList videos={listPopularVideos(store.videos)} />
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
      </SubPageContainer>
    </PageContainer>
  );
});

export default LibraryPage;
