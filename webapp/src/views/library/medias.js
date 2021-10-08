import {
  Avatar,
  Grid,
  List,
  ListItem,
  ListItemAvatar,
} from "@material-ui/core";
import { makeStyles, createStyles } from "@material-ui/core/styles";

import { observer } from "mobx-react-lite";

import { useAppStore } from "components/app_context";

const useStyles = makeStyles(() =>
  createStyles({
    listContainer: {
      height: `calc(100% - 65px)`,
      overflow: "auto",
    },
  })
);

const MediasPage = observer(() => {
  const store = useAppStore();
  const classes = useStyles();

  return (
    <List className={classes.listContainer}>
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
