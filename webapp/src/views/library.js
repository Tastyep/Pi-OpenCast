import React, { useEffect } from "react";

import { Box, Divider, Stack, Tabs, Tab, Typography } from "@mui/material";

import { Link, Outlet, useLocation } from "react-router-dom";

import { observer } from "mobx-react-lite";

import { useMediaQuery } from "react-responsive";
import { SIZES } from "constants.js";

import AlbumsPage from "views/library/albums";
import ArtistsPage from "views/library/artists";
import MediasPage from "views/library/medias";
import PlaylistsPage from "views/library/playlists";

import { useAppStore } from "providers/app_context";
import VideoList from "components/video_list";

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

  return (
    <Box sx={{ width: "92%" }}>
      <Typography variant="h6" sx={{ paddingTop: "32px" }}>
        Recent activity
      </Typography>
      <VideoList videos={listLastPlayedVideos(store.videos)} count={10} />
      <Divider
        sx={{
          margin: "32px 0px",
        }}
      />
      <Typography variant="h6">Most played</Typography>
      <VideoList videos={listPopularVideos(store.videos)} count={10} />
    </Box>
  );
});

const LibraryLayout = () => {
  const location = useLocation();
  const store = useAppStore();

  const isSmallDevice = useMediaQuery({
    maxWidth: SIZES.small.max,
  });
  const pageLayout = { width: isSmallDevice ? "100%" : "92%" };

  let count = 0;
  const pathname = location.pathname;
  for (let i = 0; i < pathname.length; count += pathname[i++] === "/");
  const displayTabs = count < 3;

  useEffect(() => {
    store.loadVideos();
  }, [store]);

  return (
    <Stack direction="column" alignItems="center" sx={{ height: "100%" }}>
      {displayTabs && (
        <Box sx={pageLayout}>
          <Tabs
            value={location.pathname}
            variant="scrollable"
            allowScrollButtonsMobile
          >
            <Tab
              label="Overview"
              value={"/library"}
              to={"/library"}
              component={Link}
            />
            <Tab
              label="Playlists"
              value={"/library/playlists"}
              to={"playlists"}
              component={Link}
            />
            <Tab
              label="Artists"
              value={"/library/artists"}
              to={"artists"}
              component={Link}
            />
            <Tab
              label="Albums"
              value={"/library/albums"}
              to={"albums"}
              component={Link}
            />
            <Tab
              label="Titles"
              value={"/library/medias"}
              to={"medias"}
              component={Link}
            />
          </Tabs>
          <Divider />
        </Box>
      )}
      <Stack
        alignItems="center"
        sx={{ overflow: "auto", width: "100%", height: "100%" }}
      >
        <Outlet />
      </Stack>
    </Stack>
  );
};

export {
  LibraryLayout,
  LibraryPage,
  PlaylistsPage,
  ArtistsPage,
  AlbumsPage,
  MediasPage,
};
