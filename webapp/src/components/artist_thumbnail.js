import { useState } from "react";

import Stack from "@mui/material/Stack";
import IconButton from "@mui/material/IconButton";
import { styled } from "@mui/material/styles";

import ArtTrackIcon from "@mui/icons-material/ArtTrack";
import MoreVertIcon from "@mui/icons-material/MoreVert";
import PlayArrowIcon from "@mui/icons-material/PlayArrow";

import { Link } from "react-router-dom";
import { observer } from "mobx-react";

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

const ArtistThumbnail = observer(({ artist }) => {
  if (!artist.thumbnail) {
    return (
      <ArtTrackIcon
        sx={{
          height: "64%",
          width: "64%",
          color: "rgba(0,0,0,0.6)",
          caretColor: "transparent",
        }}
      />
    );
  }

  return (
    <img
      alt={artist.name}
      src={artist.thumbnail}
      style={{ width: "100%", height: "100%" }}
    />
  );
});

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
      to={artist.id}
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
      <ArtistThumbnail artist={artist} />
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
