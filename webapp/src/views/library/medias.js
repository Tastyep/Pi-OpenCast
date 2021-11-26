import { observer } from "mobx-react-lite";

import { useMediaQuery } from "react-responsive";
import { SIZES } from "constants.js";

import { useAppStore } from "components/app_context";
import { VirtualizedMediaList } from "components/media_list";

const MediasPage = observer(() => {
  const store = useAppStore();

  const isSmallDevice = useMediaQuery({
    maxWidth: SIZES.small.max,
  });
  let listStyle = { flex: 1, width: "100%", minHeight: "0px" };
  if (!isSmallDevice) {
    listStyle["width"] = "92%";
  }

  const videos = Object.values(store.videos);
  return <VirtualizedMediaList videos={videos} style={listStyle} />;
});

export default MediasPage;
