import { IconButton, List, ListItem, Stack, Typography } from "@mui/material";
import MoreVertIcon from "@mui/icons-material/MoreVert";

import { styled } from "@mui/material/styles";

import { Link } from "react-router-dom";

import { observer } from "mobx-react-lite";

import { useAppStore } from "components/app_context";

const AlbumItemContainer = styled(ListItem)({
  flexGrow: 0,
  flowShrink: 1,
  width: "256px",
  flexDirection: "column",
  maxWidth: "50%",
});

const AlbumItemBar = styled((props) => <Stack {...props} />)({
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
  overflow: "hidden",
});

const AlbumsPage = observer(() => {
  const store = useAppStore();
  const albums = Object.values(store.albums());

  if (albums.length === 0) {
    return null;
  }

  albums.sort((a, b) => {
    return a.name.localeCompare(b.name);
  });
  return (
    <>
      <List sx={{ display: "flex", flexDirection: "row", flexWrap: "wrap" }}>
        {albums.map((album, _) => (
          <AlbumItemContainer key={album.name}>
            <Link
              to={"/albums/" + album.name}
              style={{
                display: "flex",
                height: "100%",
                width: "100%",
                borderRadius: "8px",
                overflow: "hidden",
              }}
            >
              <img
                src={album.thumbnail}
                alt={album.name}
                style={{
                  height: "100%",
                  width: "100%",
                  objectFit: "cover",
                  aspectRatio: "1/1",
                }}
              />
            </Link>
            <AlbumItemBar>
              <div style={{ marginRight: "auto", visibility: "hidden" }}></div>
              <div style={{ marginRight: "auto", visibility: "hidden" }}></div>
              <div style={{ marginRight: "auto", visibility: "hidden" }}></div>
              <Typography
                sx={{
                  color: "#FFFFFF",
                  padding: "0px 16px",
                  whiteSpace: "nowrap",
                  overflow: "hidden",
                }}
              >
                {album.name}
              </Typography>
              <div style={{ marginRight: "auto", visibility: "hidden" }}></div>
              <IconButton sx={{ marginLeft: "auto" }} onClick={(e) => {}}>
                <MoreVertIcon sx={{ marginLeft: "auto", color: "#FFFFFF" }} />
              </IconButton>
            </AlbumItemBar>
          </AlbumItemContainer>
        ))}
      </List>
    </>
  );
});

export default AlbumsPage;
