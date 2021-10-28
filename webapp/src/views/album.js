import { Box, Divider, List, Typography } from "@mui/material";

import { useParams } from "react-router-dom";

import { observer } from "mobx-react-lite";

import { useAppStore } from "components/app_context";
import MediaItem from "components/media_item";

const pluralize = require("pluralize");

const AlbumPage = observer(() => {
  const store = useAppStore();
  const { name } = useParams();
  const album = store.albums()[name];

  if (!album) {
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
        <Box
          sx={{
            width: "128px",
            height: "128px",
            marginRight: "32px",
            borderRadius: "8px",
            overflow: "hidden",
          }}
        >
          <img
            src={album.thumbnail}
            alt={name}
            style={{
              height: "100%",
              width: "100%",
              objectFit: "cover",
            }}
          />
        </Box>
        <Box>
          <Typography variant="h4">{name}</Typography>
          <Typography>
            {pluralize("media", album.videos.length, true)}
          </Typography>
        </Box>
      </Box>
      <Divider />
      <Box
        sx={{
          height: "100%",
          width: "100%",
          overflow: "auto",
        }}
      >
        <List sx={{ height: "100%", width: "100%", padding: "0px" }}>
          {album.videos.map((video) => (
            <MediaItem key={video.id} video={video} />
          ))}
        </List>
      </Box>
    </Box>
  );
});

export default AlbumPage;
