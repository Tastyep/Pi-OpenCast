import LinearProgress from "@mui/material/LinearProgress";

import { useAppStore } from "./app_context";
import { observer } from "mobx-react-lite";

const PlayerProgress = observer(() => {
  const store = useAppStore();
  const media = store.videos[store.player.videoId];

  if (!media) {
    return null;
  }

  return <LinearProgress variant="determinate" value={media.playTime} />;
});

export default PlayerProgress;
