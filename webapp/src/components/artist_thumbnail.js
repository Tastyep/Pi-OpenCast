import { useState } from "react";

import Stack from "@mui/material/Stack";
import IconButton from "@mui/material/IconButton";
import ImageList from "@mui/material/ImageList";
import ImageListItem from "@mui/material/ImageListItem";
import { styled } from "@mui/material/styles";

import ArtTrackIcon from "@mui/icons-material/ArtTrack";
import MoreVertIcon from "@mui/icons-material/MoreVert";
import PlayArrowIcon from "@mui/icons-material/PlayArrow";

import { Link } from "react-router-dom";

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

const ArtistThumbnail = ({ albums }) => {
  if (albums.length === 0) {
    return (
      <ArtTrackIcon
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
        <ImageListItem key={index}>
          <img
            src={albums[index % albums.length].thumbnail}
            alt={albums[index % albums.length].name}
            loading="lazy"
          />
        </ImageListItem>
      ))}
    </ImageList>
  );
};

const ArtistMenuThumbnail = (props) => {
  const { artist, isSmallDevice, isMenuOpen, menuClick, playNext } = props;
  const [hover, setHover] = useState(isSmallDevice || isMenuOpen);

  const onMenuClick = (evt) => {
    menuClick(evt);
    evt.preventDefault();
  };

  const playArtist = (evt) => {
    playNext(true);
    evt.preventDefault();
  };

  return (
    <Link
      to={encodeURIComponent(artist.name)}
      onMouseEnter={() => {
        setHover(true);
      }}
      onMouseLeave={() => {
        setHover(isMenuOpen);
      }}
      style={{
        display: "flex",
        height: "100%",
        width: "100%",
        justifyContent: "center",
        alignItems: "center",
        borderRadius: "5%",
        overflow: "hidden",
        background:
          "linear-gradient(to bottom right, #C6FFDD 0%, #FBD786 50%, #F7797D 100%)",
      }}
    >
      <ArtistThumbnail albums={artist.albums} />
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
          <ThumbnailPlayButton onClick={playArtist}>
            <PlayArrowIcon sx={{ color: "#F5F5F5", marginTop: "auto" }} />
          </ThumbnailPlayButton>
        </Stack>
      )}
    </Link>
  );
};

export { ArtistThumbnail, ArtistMenuThumbnail };
