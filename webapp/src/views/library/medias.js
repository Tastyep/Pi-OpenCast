import { List, ListItem } from "@material-ui/core";

import { observer } from "mobx-react-lite";

import { useAppStore } from "components/app_context";

const MediasPage = observer(() => {
  const store = useAppStore();

  return (
    <List>
      {Object.keys(store.videos).map((videoId, video) => (
        <ListItem key={videoId}>{store.videos[videoId].title}</ListItem>
      ))}
    </List>
  );
});

export default MediasPage;
