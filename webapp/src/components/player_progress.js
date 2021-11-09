import LinearProgress from "@mui/material/LinearProgress";

import { useAppStore } from "./app_context";
import { observer } from "mobx-react-lite";

const PlayerProgress = observer(() => {
  const store = useAppStore();
  const media = store.videos[store.player.videoId];

  if (!media || media.duration === 0) {
    return null;
  }

  return (
    <LinearProgress
      variant="determinate"
      value={(100 * media.playTime) / media.duration}
    />
  );
});

export default PlayerProgress;
