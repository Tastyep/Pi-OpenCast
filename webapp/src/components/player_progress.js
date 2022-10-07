import Slider from "@mui/material/Slider";

import { observer } from "mobx-react-lite";

import { useAppStore } from "./app_context";
import playerAPI from "services/api/player";
import snackBarHandler from "services/api/error";

const PlayerProgress = observer(({ height = 4 }) => {
  const store = useAppStore();
  const media = store.videos[store.player.videoId];

  if (!media || media.duration === 0) {
    return null;
  }

  const updateMediaTime = (_, value) => {
    media.setPlayTime(1000 * value);
  };

  const seekMedia = (_, value) => {
    playerAPI.seekMedia(1000 * value).catch(snackBarHandler(store));
  };

  const thumbHeight = height * 2;
  const thumbWidth = thumbHeight / 2;
  const activeThumbHeight = thumbHeight + thumbHeight / 2;
  const activeThumbWidth = thumbWidth + thumbWidth / 2;

  return (
    <Slider
      min={0}
      step={1}
      max={media.duration}
      value={media.playTime / 1000}
      onChange={updateMediaTime}
      onChangeCommitted={seekMedia}
      sx={{
        display: "block",
        borderRadius: "0px",
        color: "rgba(89,123,157,0.87)",
        height: { height },
        padding: "0px",
        "@media (pointer: coarse)": {
          padding: "0px",
        },
        "& .MuiSlider-thumb": {
          width: thumbWidth,
          height: thumbHeight,
          borderRadius: "0px",
          transition: "0.3s cubic-bezier(.47,1.64,.41,.8)",
          "&:before": {
            boxShadow: "0 2px 8px 0 rgba(0,0,0,0.4)",
          },
          "&:hover, &.Mui-focusVisible": {
            boxShadow: `0px 0px 0px 8px ${"rgb(0 0 0 / 16%)"}`,
          },
          "&.Mui-active": {
            width: activeThumbWidth,
            height: activeThumbHeight,
          },
        },
        "& .MuiSlider-rail": {
          opacity: 0.28,
        },
      }}
    />
  );
});

export default PlayerProgress;
