import { Avatar, Grid, List, ListItem, ListItemAvatar } from "@mui/material";
import { styled } from "@mui/material/styles";

import { observer } from "mobx-react-lite";

import { useAppStore } from "components/app_context";

const PREFIX = "MediasPage";

const classes = {
  listContainer: `${PREFIX}-listContainer`,
};

const StyledList = styled(List)(() => ({
  [`&.${classes.listContainer}`]: {
    height: `calc(100% - 65px)`,
    overflow: "auto",
  },
}));

const MediasPage = observer(() => {
  const store = useAppStore();

  return (
    <StyledList className={classes.listContainer}>
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
    </StyledList>
  );
});

export default MediasPage;
