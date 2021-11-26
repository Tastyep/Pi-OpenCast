import React, { useMemo } from "react";

import List from "@mui/material/List";

import { observer } from "mobx-react-lite";

import { useMediaQuery } from "react-responsive";
import { SIZES } from "constants.js";

import { Virtuoso } from "react-virtuoso";

import { useAppStore } from "components/app_context";
import { MediaItem } from "components/media_item";

const VirtualizedMediaList = observer((props) => {
  const store = useAppStore();
  const { children, videos, style, mediaProps, mediaOptions = null } = props;

  console.log("VIDEOS: ", videos);

  const isSmallDevice = useMediaQuery({
    maxWidth: SIZES.small.max,
  });

  const Components = useMemo(() => {
    return {
      List: React.forwardRef(({ style, children }, listRef) => {
        return (
          <List
            style={{ padding: 0, ...style, margin: 0 }}
            component="div"
            ref={listRef}
          >
            {children}
          </List>
        );
      }),
    };
  }, []);

  const itemContent = (idx, video) => (
    <MediaItem
      key={video.id}
      idx={idx}
      isSmallDevice={isSmallDevice}
      video={video}
      isActive={video.id === store.player.videoId}
      {...mediaProps}
    >
      {mediaOptions && mediaOptions(video)}
      {children}
    </MediaItem>
  );

  return (
    <Virtuoso
      data={videos}
      style={style}
      components={Components}
      itemContent={itemContent}
    />
  );
});

export { VirtualizedMediaList };
