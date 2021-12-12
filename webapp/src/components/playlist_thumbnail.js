import { useState } from "react";

import { ImageList, ImageListItem } from "@mui/material";
import IconButton from "@mui/material/IconButton";
import Stack from "@mui/material/Stack";
import { styled } from "@mui/material/styles";

import QueueMusicIcon from "@mui/icons-material/QueueMusic";
import MoreVertIcon from "@mui/icons-material/MoreVert";
import PlayArrowIcon from "@mui/icons-material/PlayArrow";

const ThumbnailPlayButton = styled(IconButton)({
  display: "flex",
  justifyContent: "center",
  alignItems: "center",
  position: "absolute",
  bottom: "52px",
  right: "14px",
  background: "rgba(0,0,0,0.33)",
  "&:hover": {
    background: "rgba(0,0,0,0.6)",
    transform: "scale(1.3)",
  },
});

const listPopularVideos = (videos) => {
  return videos
    .sort((a, b) => {
      return a.totalPlayingDuration < b.totalPlayingDuration;
    })
    .slice(0, 4);
};

const PlaylistThumbnail = ({ videos }) => {
  const popVideos = listPopularVideos(Array.from(videos));

  if (popVideos.length === 0) {
    return (
      <QueueMusicIcon
        sx={{ height: "64%", width: "64%", color: "rgba(0,0,0,0.6)" }}
      />
    );
  }
  return (
    <ImageList
      cols={2}
      gap={0}
      sx={{ width: "100%", height: "100%", aspectRatio: "1/1", margin: "0px" }}
    >
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
  );
};

const PlaylistMenuThumbnail = (props) => {
  const { videos, isSmallDevice, isMenuOpen, menuClick, playNext } = props;
  const [hover, setHover] = useState(isSmallDevice || isMenuOpen);

  const onMenuClick = (evt) => {
    menuClick(evt);
    evt.preventDefault();
  };

  const playList = (evt) => {
    playNext(true);
    evt.preventDefault();
  };

  return (
    <Stack
      style={{
        width: "100%",
        height: "100%",
        justifyContent: "center",
        alignItems: "center",
      }}
      onMouseEnter={() => {
        setHover(true);
      }}
      onMouseLeave={() => {
        setHover(isMenuOpen);
      }}
    >
      <PlaylistThumbnail videos={videos} />
      {hover && (
        <Stack
          justifyContent="right"
          sx={{
            height: "100%",
            width: "100%",
            position: "absolute",
            borderRadius: "8px 8px 0px 0px",
            background:
              "linear-gradient(180deg, rgba(0,0,0,0.5) 0%, rgba(0,0,0,0) 25%, rgba(0,0,0,0) 100%)",
          }}
        >
          <IconButton
            sx={{ position: "absolute", top: "8px", right: "8px" }}
            onClick={onMenuClick}
          >
            <MoreVertIcon sx={{ marginLeft: "auto", color: "#FFFFFF" }} />
          </IconButton>
          <ThumbnailPlayButton onClick={playList}>
            <PlayArrowIcon sx={{ color: "#F5F5F5", marginTop: "auto" }} />
          </ThumbnailPlayButton>
        </Stack>
      )}
    </Stack>
  );
};

export { PlaylistThumbnail, PlaylistMenuThumbnail };
