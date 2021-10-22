import { useState } from "react";

import Box from "@mui/material/Box";
import IconButton from "@mui/material/IconButton";
import ImageList from "@mui/material/ImageList";
import ImageListItem from "@mui/material/ImageListItem";
import List from "@mui/material/List";
import ListItem from "@mui/material/ListItem";
import ListItemIcon from "@mui/material/ListItemIcon";
import ListItemText from "@mui/material/ListItemText";
import Menu from "@mui/material/Menu";
import MenuItem from "@mui/material/MenuItem";
import Stack from "@mui/material/Stack";
import Typography from "@mui/material/Typography";

import MoreVertIcon from "@mui/icons-material/MoreVert";
import ShuffleIcon from "@mui/icons-material/Shuffle";

import { styled } from "@mui/material/styles";

import { Link } from "react-router-dom";

import { observer } from "mobx-react-lite";

import { useAppStore } from "components/app_context";

const ArtistItemContainer = styled(ListItem)({
  flexGrow: 0,
  flowShrink: 1,
  flexBasis: "256px",
  flexDirection: "column",
  maxWidth: "50%",
});

const ArtistItemBar = styled((props) => <Stack {...props} />)({
  flexDirection: "row",
  alignItems: "center",
  justifyContent: "center",
  width: "100%",
  height: "40px",
  position: "relative",
  transform: "translate(0px, -40px)",
  marginBottom: "-40px",
  backgroundColor: "rgba(0, 0, 0, 0.6)",
  borderBottomLeftRadius: "8px",
  borderBottomRightRadius: "8px",
});

const ArtistThumbnail = ({ albums }) => {
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
      <ImageList cols={2} gap={0} sx={{ width: "100%", height: "100%" }}>
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
    </Box>
  );
};

const ArtistItem = ({ artist }) => {
  const [anchor, setAnchor] = useState(null);
  const isMenuOpen = Boolean(anchor);

  const closeMenu = () => {
    setAnchor(null);
  };

  return (
    <ArtistItemContainer>
      <Link
        to={"/artists/" + artist.name}
        style={{ width: "100%", aspectRatio: "1/1" }}
      >
        <ArtistThumbnail albums={artist.albums} />
      </Link>
      <ArtistItemBar>
        <div style={{ marginRight: "auto", visibility: "hidden" }}></div>
        <div style={{ marginRight: "auto", visibility: "hidden" }}></div>
        <div style={{ marginRight: "auto", visibility: "hidden" }}></div>
        <Typography sx={{ color: "#FFFFFF" }}>{artist.name}</Typography>
        <div style={{ marginRight: "auto", visibility: "hidden" }}></div>
        <IconButton
          sx={{ marginLeft: "auto" }}
          onClick={(e) => {
            setAnchor(e.currentTarget);
          }}
        >
          <MoreVertIcon sx={{ marginLeft: "auto", color: "#FFFFFF" }} />
        </IconButton>
      </ArtistItemBar>
      <Menu
        id="artist-menu"
        anchorEl={anchor}
        open={isMenuOpen}
        onClose={closeMenu}
        MenuListProps={{
          "aria-labelledby": "basic-button",
        }}
        transformOrigin={{ horizontal: "right", vertical: "top" }}
        anchorOrigin={{ horizontal: "right", vertical: "bottom" }}
      >
        <MenuItem onClick={() => {}}>
          <ListItemIcon>
            <ShuffleIcon />
          </ListItemIcon>
          <ListItemText>placeholder</ListItemText>
        </MenuItem>
      </Menu>
    </ArtistItemContainer>
  );
};

const ArtistsPage = observer(() => {
  const store = useAppStore();
  const artists = Object.values(store.artists());

  if (artists.length === 0) {
    return null;
  }

  return (
    <>
      <List sx={{ display: "flex", flexDirection: "row", flexWrap: "wrap" }}>
        {artists.map((artist, _) => (
          <ArtistItem key={artist.name} artist={artist} />
        ))}
      </List>
    </>
  );
});

export default ArtistsPage;
