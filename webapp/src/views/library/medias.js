import {
  Avatar,
  List,
  ListItem,
  ListItemAvatar,
  ListItemText,
  Stack,
} from "@mui/material";

import Media from "react-media";
import { SIZES } from "constants.js";

import { observer } from "mobx-react-lite";

import { duration_to_hms } from "services/duration";

import { useAppStore } from "components/app_context";

const MediaItem = ({ video }) => {
  return (
    <ListItem sx={{ width: "100%" }}>
      <ListItemAvatar>
        <Avatar alt={video.title} src={video.thumbnail} />
      </ListItemAvatar>
      <Stack direction="row" alignItems="center" sx={{ width: "100%" }}>
        <ListItemText>{video.title}</ListItemText>
        <Media queries={{ medium: { minWidth: SIZES.medium.min } }}>
          {(matches) =>
            matches.medium && <ListItemText> {video.title}</ListItemText>
          }
        </Media>

        <ListItemText
          primary={duration_to_hms(video.duration)}
          sx={{ textAlign: "right" }}
        />
      </Stack>
    </ListItem>
  );
};

const MediasPage = observer(() => {
  const store = useAppStore();

  return (
    <List sx={{ height: "100%", width: "100%" }}>
      {Object.keys(store.videos).map((videoId, _) => (
        <MediaItem key={videoId} video={store.videos[videoId]} />
      ))}
    </List>
  );
});

export default MediasPage;
