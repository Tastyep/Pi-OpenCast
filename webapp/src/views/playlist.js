import { Box, Typography } from "@mui/material";

import { useParams } from "react-router-dom";

import { observer } from "mobx-react-lite";

import { useAppStore } from "components/app_context";
import PlaylistThumbnail from "components/playlist_thumbnail";
import MediaList from "components/media_list";

const PlaylistPage = observer(() => {
  const store = useAppStore();
  const { id } = useParams();
  const playlist = store.playlists[id];
  const videos = store.playlistVideos(id);

  if (!playlist) {
    return null;
  }

  return (
    <Box sx={{ display: "flex", flexDirection: "column", height: "100%" }}>
      <Box
        sx={{
          display: "flex",
          flexDirection: "row",
          alignItems: "center",
          marginTop: "32px",
          marginBottom: "32px",
          marginLeft: "16px",
        }}
      >
        <Box sx={{ marginRight: "32px" }}>
          <PlaylistThumbnail videos={videos} />
        </Box>
        <Box>
          <Typography variant="h4">{playlist.name}</Typography>
          <Typography>{videos.length} medias</Typography>
        </Box>
      </Box>
      <Box sx={{ overflow: "auto" }}>
        <MediaList medias={videos} />
      </Box>
    </Box>
  );
});

export default PlaylistPage;
