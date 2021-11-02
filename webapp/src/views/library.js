import React from "react";

import { Divider, Tabs, Tab, Typography } from "@mui/material";
import { styled } from "@mui/material/styles";

import {
  Switch,
  Route,
  Link,
  useLocation,
  useRouteMatch,
} from "react-router-dom";

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

const listLastPlayedVideos = (videos) => {
  return Object.values(videos)
    .sort((a, b) => {
      return new Date(a.lastPlay) < new Date(b.lastPlay);
    })
    .slice(0, 10);
};

const listPopularVideos = (videos) => {
  return Object.values(videos)
    .sort((a, b) => {
      return a.totalPlayingDuration < b.totalPlayingDuration;
    })
    .slice(0, 10);
};

const LibraryPage = observer(() => {
  const store = useAppStore();

  let { path, url } = useRouteMatch();
  let location = useLocation();

  return (
    <PageContainer>
      <Tabs
        value={location.pathname}
        variant="scrollable"
        allowScrollButtonsMobile
      >
        <Tab label="Overview" value={url} to={`${url}`} component={Link} />
        <Tab
          label="Playlists"
          value={`${url}/playlists`}
          to={`${url}/playlists`}
          component={Link}
        />
        <Tab
          label="Artists"
          value={`${url}/artists`}
          to={`${url}/artists`}
          component={Link}
        />
        <Tab
          label="Albums"
          value={`${url}/albums`}
          to={`${url}/albums`}
          component={Link}
        />
        <Tab
          label="Titles"
          value={`${url}/medias`}
          to={`${url}/medias`}
          component={Link}
        />
      </Tabs>
      <Divider />
      <SubPageContainer>
        <Switch>
          <Route exact path={path}>
            <Typography variant="h6" sx={{ paddingTop: "32px" }}>
              Recent activity
            </Typography>
            <VideoList videos={listLastPlayedVideos(store.videos)} count={10} />
            <Divider
              sx={{
                margin: "32px 0px",
              }}
            />
            <Typography variant="h6" sx={{ paddingTop: "16px" }}>
              Most played
            </Typography>
            <VideoList videos={listPopularVideos(store.videos)} count={10} />
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
