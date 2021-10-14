import { List } from "@mui/material";

import { observer } from "mobx-react-lite";

import { useAppStore } from "components/app_context";
import MediaItem from "components/media_item";

const MediasPage = observer(() => {
  const store = useAppStore();

  return (
    <List sx={{ height: "100%", width: "100%" }}>
      {Object.values(store.videos).map((video) => (
        <MediaItem key={video.id} video={video} />
      ))}
    </List>
  );
});

export default MediasPage;
