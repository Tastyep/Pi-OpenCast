import List from "@mui/material/List";

import { observer } from "mobx-react-lite";

import { useMediaQuery } from "react-responsive";
import { SIZES } from "constants.js";

import { useAppStore } from "components/app_context";
import { MediaItem } from "components/media_item";

const MediasPage = observer(() => {
  const store = useAppStore();

  const isSmallDevice = useMediaQuery({
    maxWidth: SIZES.small.max,
  });
  let style = { height: `calc(100% - 16px)`, width: "100%" };
  if (!isSmallDevice) {
    style["width"] = "92%";
  }

  return (
    <List sx={style}>
      {Object.values(store.videos).map((video) => (
        <MediaItem
          key={video.id}
          playlist={null}
          video={video}
          isActive={video.id === store.player.videoId}
        />
      ))}
    </List>
  );
});

export default MediasPage;
