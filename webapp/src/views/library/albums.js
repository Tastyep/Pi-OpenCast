import { IconButton, List, ListItem, Stack, Typography } from "@mui/material";
import MoreVertIcon from "@mui/icons-material/MoreVert";

import { styled } from "@mui/material/styles";

import { Link } from "react-router-dom";

import { observer } from "mobx-react-lite";

import { useAppStore } from "components/app_context";

const AlbumItemContainer = styled(ListItem)({
  flexGrow: 0,
  flowShrink: 1,
  flexBasis: "312px",
  flexDirection: "column",
  maxWidth: "50%",
});

const AlbumItemBar = styled((props) => <Stack {...props} />)({
  flexDirection: "row",
  alignItems: "center",
  justifyContent: "center",
  width: "100%",
  position: "relative",
  transform: "translate(0px, -40px)",
  marginBottom: "-40px",
  backgroundColor: "rgba(0, 0, 0, 0.6)",
  borderBottomLeftRadius: "12px",
  borderBottomRightRadius: "12px",
  maxHeight: "40px",
  overflow: "hidden",
});

const AlbumsPage = observer(() => {
  const store = useAppStore();
  const albums = store.albums();

  console.log("ALBUMS: ", albums);
  if (albums === {}) {
    return null;
  }

  return (
    <>
      <List sx={{ display: "flex", flexDirection: "row", flexWrap: "wrap" }}>
        {Object.entries(albums).map(([name, album], _) => (
          <AlbumItemContainer key={name}>
            <Link
              to={"/albums/" + name}
              style={{
                display: "flex",
                height: "100%",
                width: "100%",
                borderRadius: "5%",
                backgroundImage: `url("${album.thumbnail}")`,
                backgroundSize: "cover",
                overflow: "hidden",
                aspectRatio: "16/9",
              }}
            >
              <div
                style={{
                  height: "100%",
                  width: "100%",
                  backgroundColor: "rgba(0,0,0,0.6)",
                }}
              >
                <img
                  src={album.thumbnail}
                  alt={name}
                  style={{
                    height: "100%",
                    width: "100%",
                    objectFit: "contain",
                  }}
                />
              </div>
            </Link>
            <AlbumItemBar>
              <div style={{ marginRight: "auto", visibility: "hidden" }}></div>
              <div style={{ marginRight: "auto", visibility: "hidden" }}></div>
              <div style={{ marginRight: "auto", visibility: "hidden" }}></div>
              <Typography sx={{ color: "#FFFFFF", padding: "0px 16px" }}>
                {name}
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
