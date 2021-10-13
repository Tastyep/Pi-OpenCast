import {
  Avatar,
  Grid,
  List,
  ListItem,
  ListItemAvatar,
  ListItemText,
  Stack,
  Typography,
} from "@mui/material";

import Media from "react-media";
import { SIZES } from "constants.js";

import { observer } from "mobx-react-lite";

import { durationToHMS } from "services/duration";

import { useAppStore } from "components/app_context";

const MediaItem = ({ video }) => {
  return (
    <ListItem sx={{ width: "100%" }}>
      <Media queries={{ large: { minWidth: SIZES.large.min } }}>
        {(matches) =>
          matches.large ? (
            <Grid container xs spacing>
              <Grid item xs>
                <Stack direction="row" alignItems="center">
                  <ListItemAvatar>
                    <Avatar alt={video.title} src={video.thumbnail} />
                  </ListItemAvatar>
                  <ListItemText>{video.title}</ListItemText>
                </Stack>
              </Grid>
              <Grid item xs alignSelf="center">
                <ListItemText sx={{ color: "#505050" }}>
                  {" "}
                  {"Artist"}
                </ListItemText>
              </Grid>
              <Grid item xs alignSelf="center">
                <ListItemText sx={{ color: "#505050" }}>
                  {" "}
                  {"Album"}
                </ListItemText>
              </Grid>
              <Grid item alignSelf="center">
                <ListItemText
                  primary={durationToHMS(video.duration)}
                  sx={{ textAlign: "right", color: "#505050" }}
                />
              </Grid>
            </Grid>
          ) : (
            <Grid container xs spacing alignItems="center">
              <Grid item xs>
                <Stack direction="row" alignItems="center">
                  <ListItemAvatar>
                    <Avatar alt={video.title} src={video.thumbnail} />
                  </ListItemAvatar>
                  <Stack>
                    <Typography>{video.title}</Typography>{" "}
                    <Typography sx={{ color: "#505050" }}>
                      {"Artist • Album"}
                    </Typography>
                  </Stack>
                </Stack>
              </Grid>
              <Grid item alignSelf="center">
                <ListItemText
                  primary={durationToHMS(video.duration)}
                  sx={{ textAlign: "right", color: "#505050" }}
                />
              </Grid>
            </Grid>
          )
        }
      </Media>
    </ListItem>
  );
};

const MediaList = observer(({ medias }) => {
  return (
    <List sx={{ height: "100%", width: "100%" }}>
      {medias.map((media) => (
        <MediaItem key={media.id} video={media} />
      ))}
    </List>
  );
});

export default MediaList;
