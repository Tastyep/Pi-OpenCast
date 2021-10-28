import { Box, Divider, List, Typography } from "@mui/material";

import { useParams } from "react-router-dom";

import { observer } from "mobx-react-lite";

import { useAppStore } from "components/app_context";
import ArtistThumbnail from "components/artist_thumbnail";
import MediaItem from "components/media_item";

const pluralize = require("pluralize");

const ArtistPage = observer(() => {
  const store = useAppStore();
  const { name } = useParams();
  const artist = store.artists()[name];

  if (!artist) {
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
          <ArtistThumbnail albums={artist.albums} />
        </Box>
        <Box>
          <Typography variant="h4">{name}</Typography>
          <Typography>
            {pluralize("media", artist.videos.length, true)}
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
          {artist.videos.map((video) => (
            <MediaItem key={video.id} video={video} />
          ))}
        </List>
      </Box>
    </Box>
  );
});

export default ArtistPage;
