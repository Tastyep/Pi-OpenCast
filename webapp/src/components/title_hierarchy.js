import { Grid, Stack, Typography } from "@mui/material";
import { styled } from "@mui/material/styles";

import { Link } from "react-router-dom";

const StyledLink = styled(Link)({
  color: "inherit",
  textDecoration: "none",
});

const TitleHierarchy = (props) => {
  const {
    artist,
    album,
    video,
    displayPlaceholders = true,
    direction = "row",
    align = "left",
  } = props;

  const artistBlock = artist ? (
    <StyledLink to={`/artists/${artist.id}`}>{artist.name}</StyledLink>
  ) : displayPlaceholders ? (
    "Artist"
  ) : null;

  const albumBlock = album ? (
    <StyledLink to={`/albums/${album.id}`}>{album.name}</StyledLink>
  ) : displayPlaceholders ? (
    "Album"
  ) : null;

  if (direction === "row") {
    return (
      <Grid
        container
        direction="row"
        sx={{
          flexWrap: "nowrap",
          color: "#505050",
          minWidth: "0px",
          width: "auto",
        }}
      >
        {artistBlock && (
          <Grid item zeroMinWidth>
            <Typography noWrap>{artistBlock}</Typography>
          </Grid>
        )}
        {albumBlock && (
          <Grid item zeroMinWidth>
            <Stack direction="row">
              {artistBlock && (
                <Typography sx={{ padding: "0px 4px" }}>•</Typography>
              )}
              <Typography noWrap>{albumBlock}</Typography>
            </Stack>
          </Grid>
        )}
        <Grid item zeroMinWidth>
          <Stack direction="row">
            {(albumBlock || artistBlock) && (
              <Typography sx={{ padding: "0px 4px" }}>•</Typography>
            )}
            <Typography noWrap>{video.title}</Typography>
          </Stack>
        </Grid>
      </Grid>
    );
  }

  return (
    <Stack direction="column">
      {artistBlock && (
        <Typography noWrap align={align}>
          {artistBlock}
        </Typography>
      )}
      {albumBlock && (
        <Typography noWrap align={align}>
          {albumBlock}
        </Typography>
      )}
      <Typography noWrap align={align}>
        {video.title}
      </Typography>
    </Stack>
  );
};

export default TitleHierarchy;
