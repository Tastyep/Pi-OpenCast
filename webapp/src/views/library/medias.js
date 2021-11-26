import React, { useState, useMemo } from "react";

import List from "@mui/material/List";

import { observer } from "mobx-react-lite";

import { useMediaQuery } from "react-responsive";
import { SIZES } from "constants.js";

import { Virtuoso } from "react-virtuoso";

import { useAppStore } from "components/app_context";
import { MediaItem } from "components/media_item";

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
      playlist={null}
      video={video}
      isActive={video.id === store.player.videoId}
    />
  );

  return (
    <Virtuoso
      data={videos}
      style={listStyle}
      components={Components}
      itemContent={itemContent}
    />
  );
});

export default MediasPage;
