import { Avatar, Grid, List, ListItem, ListItemAvatar } from "@mui/material";

import { observer } from "mobx-react-lite";

import { useAppStore } from "components/app_context";

const MediasPage = observer(() => {
  const store = useAppStore();

  return (
    <List sx={{ height: "100%" }}>
      {Object.keys(store.videos).map((videoId, _) => (
        <ListItem key={videoId}>
          <ListItemAvatar>
            <Avatar
              alt={store.videos[videoId].title}
              src={store.videos[videoId].thumbnail}
            />
          </ListItemAvatar>
          <Grid container>
            <Grid item>{store.videos[videoId].title}</Grid>
            <Grid item>{store.videos[videoId].title}</Grid>
          </Grid>
        </ListItem>
      ))}
    </List>
  );
});

export default MediasPage;
