import React, { useState } from "react";

import { Stack, Slider, Button } from "@mui/material";
import { useTheme } from "@mui/material/styles";
import VolumeUp from "@mui/icons-material/VolumeUp";
import VolumeOff from "@mui/icons-material/VolumeOff";

import playerAPI from "services/api/player";
import { useAppStore } from "./app_context";
import { observer } from "mobx-react-lite";

const VolumeControl = observer(() => {
  const store = useAppStore();
  const theme = useTheme();
  const [oldVolume, setOldVolume] = useState(store.player.volume);

  const handleCommit = (_, value) => {
    playerAPI.updateVolume(value);
  };

  const handleClick = () => {
    if (store.player.volume === 0) {
      let volume = oldVolume;
      if (!oldVolume) {
        volume = 50;
      }
      store.player.setVolume(volume);
      playerAPI.updateVolume(volume);
      return;
    }
    setOldVolume(store.player.volume);
    store.player.setVolume(0);
    playerAPI.updateVolume(0);
  };

  if (store.player.volume === undefined) {
    return null;
  }

  return (
    <Stack
      direction="row"
      justifyContent="end"
      alignItems="center"
      sx={{ minWidth: "160px" }}
    >
      <Slider
        size="small"
        value={store.player.volume}
        valueLabelDisplay="auto"
        aria-labelledby="continuous-slider"
        sx={{
          color: theme.palette.mode === "dark" ? "#fff" : "rgba(0,0,0,0.87)",
          "& .MuiSlider-track": {
            border: "none",
          },
          "& .MuiSlider-thumb": {
            width: 16,
            height: 16,
            backgroundColor: "#fff",
            "&:before": {
              boxShadow: "0 4px 8px rgba(0,0,0,0.4)",
            },
            "&:hover, &.Mui-focusVisible, &.Mui-active": {
              boxShadow: "none",
            },
          },
        }}
        onChange={(_, value) => {
          store.player.setVolume(value);
        }}
        onChangeCommitted={handleCommit}
      />
      <Button
        size="small"
        sx={{
          color: theme.palette.mode === "dark" ? "#fff" : "rgba(0,0,0,0.87)",
          minWidth: "0px",
          marginLeft: "8px",
        }}
        onClick={handleClick}
      >
        {(store.player.volume === 0 && <VolumeOff />) || <VolumeUp />}
      </Button>
    </Stack>
  );
});

export default VolumeControl;
