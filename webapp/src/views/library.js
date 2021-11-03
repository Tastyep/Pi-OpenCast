import React from "react";

import { Box, Divider, Stack, Tabs, Tab, Typography } from "@mui/material";
import { styled } from "@mui/material/styles";

import {
  Switch,
  Route,
  Link,
  useLocation,
  useRouteMatch,
} from "react-router-dom";

import { observer } from "mobx-react-lite";

import { useMediaQuery } from "react-responsive";
import { SIZES } from "constants.js";

import AlbumsPage from "views/library/albums";
import ArtistsPage from "views/library/artists";
import MediasPage from "views/library/medias";
import PlaylistsPage from "views/library/playlists";

import { useAppStore } from "components/app_context";
import VideoList from "components/video_list";

const SubPageContainer = styled((props) => <Box {...props} />)({
  display: "flex",
  height: `calc(100% - 50px)`,
  justifyContent: "center",
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

  const isSmallDevice = useMediaQuery({
    maxWidth: SIZES.small.max,
  });
  const pageLayout = { width: isSmallDevice ? "100%" : "92%" };
  const subPageLayout = { width: isSmallDevice ? "92%" : "100%" };

  console.log("PAGE ", pageLayout, " sub ", subPageLayout);

  return (
    <Stack direction="column" alignItems="center" sx={{ height: "100%" }}>
      <Box sx={pageLayout}>
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
      </Box>
      <SubPageContainer sx={pageLayout}>
        <Switch>
          <Route exact path={path}>
            <Box sx={subPageLayout}>
              <Typography variant="h6" sx={{ paddingTop: "32px" }}>
                Recent activity
              </Typography>
              <VideoList
                videos={listLastPlayedVideos(store.videos)}
                count={10}
              />
              <Divider
                sx={{
                  margin: "32px 0px",
                }}
              />
              <Typography variant="h6">Most played</Typography>
              <VideoList videos={listPopularVideos(store.videos)} count={10} />
            </Box>
          </Route>
          <Route path={`${path}/playlists`}>
            <Box sx={subPageLayout}>
              <PlaylistsPage />
            </Box>
          </Route>
          <Route path={`${path}/artists`}>
            <Box sx={subPageLayout}>
              <ArtistsPage />
            </Box>
          </Route>
          <Route path={`${path}/albums`}>
            <Box sx={subPageLayout}>
              <AlbumsPage />
            </Box>
          </Route>
          <Route path={`${path}/medias`}>
            <MediasPage />
          </Route>
        </Switch>
      </SubPageContainer>
    </Stack>
  );
});

export default LibraryPage;
