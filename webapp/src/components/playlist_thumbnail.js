import { Box, ImageList, ImageListItem } from "@mui/material";
import PlaylistPlayIcon from "@mui/icons-material/PlaylistPlay";

const listPopularVideos = (videos) => {
  return videos
    .sort((a, b) => {
      return a.totalPlayingDuration < b.totalPlayingDuration;
    })
    .slice(0, 4);
};

const PlaylistThumbnail = ({ videos }) => {
  const popVideos = listPopularVideos(videos);

  return (
    <Box
      sx={{
        display: "flex",
        height: "100%",
        width: "100%",
        alignItems: "center",
        justifyContent: "center",
        backgroundColor: "#F0F0F0",
        borderRadius: "5%",
        overflow: "hidden",
      }}
    >
      {popVideos.length > 0 ? (
        <ImageList cols={2} gap={0} sx={{ width: "100%", height: "100%" }}>
          {[0, 1, 2, 3].map((index) => (
            <ImageListItem key={index} sx={{ aspectRatio: "1/1" }}>
              <img
                src={popVideos[index % popVideos.length].thumbnail}
                alt={popVideos[index % popVideos.length].title}
                loading="lazy"
              />
            </ImageListItem>
          ))}
        </ImageList>
      ) : (
        <PlaylistPlayIcon
          sx={{
            width: "50%",
            height: "50%",
            color: "#707070",
          }}
        />
      )}
    </Box>
  );
};

export default PlaylistThumbnail;
