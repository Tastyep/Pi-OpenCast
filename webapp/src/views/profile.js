import React from "react";

import { Box, Divider, Stack, Tabs, Tab, Typography } from "@mui/material";

import { observer } from "mobx-react-lite";

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

const ProfilePage = observer(() => {
  const store = useAppStore();

  return (
    <Stack direction="column" sx={{ overflowX: "hidden", overflowY: "auto" }}>
      <Typography variant="h6" sx={{ paddingTop: "32px" }}>
        Recent activity
      </Typography>
      <Box sx={{ display: "flex" }}>
        <VideoList videos={listLastPlayedVideos(store.videos)} count={10} />
      </Box>
      <Divider
        sx={{
          margin: "32px 0px",
        }}
      />
      <Typography variant="h6">Most played</Typography>
      <Box sx={{ display: "flex" }}>
        <VideoList videos={listPopularVideos(store.videos)} count={10} />
      </Box>
    </Stack>
  );
});

export default ProfilePage;
