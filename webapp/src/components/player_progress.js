import Slider from "@mui/material/Slider";

import { observer } from "mobx-react-lite";

import { useAppStore } from "./app_context";
import playerAPI from "services/api/player";
import snackBarHandler from "services/api/error";

const PlayerProgress = observer(() => {
  const store = useAppStore();
  const media = store.videos[store.player.videoId];

  if (!media || media.duration === 0) {
    return null;
  }

  const updateMediaTime = (_, value) => {
    playerAPI.seekMedia(1000 * value).catch(snackBarHandler(store));
  };

  return (
    <Slider
      min={0}
      step={1}
      max={media.duration}
      value={media.playTime}
      onChange={updateMediaTime}
    />
  );
});

export default PlayerProgress;
