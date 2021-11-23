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
  let style = { flex: 1, width: "100%", minHeight: "0px" };
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
