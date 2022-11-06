import IconButton from "@mui/material/IconButton";

import PauseIcon from "@mui/icons-material/Pause";
import PlayArrowIcon from "@mui/icons-material/PlayArrow";
import AddCircleOutlineIcon from "@mui/icons-material/AddCircleOutline";
import RemoveCircleOutlineIcon from "@mui/icons-material/RemoveCircleOutline";
import ClosedCaptionIcon from "@mui/icons-material/ClosedCaption";
import ClosedCaptionDisabledIcon from "@mui/icons-material/ClosedCaptionDisabled";

import { observer } from "mobx-react-lite";

import { useAppStore } from "providers/app_context";

import playerAPI from "services/api/player";
import snackBarHandler from "services/api/error";

const PausePlayButton = observer((props) => {
  const store = useAppStore();
  const isPlayerPlaying = store.player.isPlaying;
  const { buttonSize = "medium", iconColor, iconSize = "medium", sx } = props;

  return (
    <IconButton
      size={buttonSize}
      color={iconColor}
      sx={sx}
      onClick={() => playerAPI.pauseMedia().catch(snackBarHandler(store))}
    >
      {isPlayerPlaying ? (
        <PauseIcon fontSize={iconSize} />
      ) : (
        <PlayArrowIcon fontSize={iconSize} />
      )}
    </IconButton>
  );
});

const SubtitleButtons = observer((props) => {
  const { iconColor, iconSize = "medium", buttonSize = "medium" } = props;
  const store = useAppStore();

  return (
    <>
      <IconButton
        size={buttonSize}
        color={iconColor}
        onClick={() =>
          playerAPI
            .seekSubtitle(store.player.subDelay - 100)
            .catch(snackBarHandler(store))
        }
      >
        <RemoveCircleOutlineIcon fontSize={iconSize} />
      </IconButton>
      <IconButton
        size={iconSize}
        color={iconColor}
        onClick={() => playerAPI.toggleSubtitle().catch(snackBarHandler(store))}
      >
        {store.player.subState ? (
          <ClosedCaptionIcon fontSize={iconSize} />
        ) : (
          <ClosedCaptionDisabledIcon fontSize={iconSize} />
        )}
      </IconButton>
      <IconButton
        size={buttonSize}
        color={iconColor}
        onClick={() =>
          playerAPI
            .seekSubtitle(store.player.subDelay + 100)
            .catch(snackBarHandler(store))
        }
      >
        <AddCircleOutlineIcon fontSize={iconSize} />
      </IconButton>
    </>
  );
});

export { PausePlayButton, SubtitleButtons };
