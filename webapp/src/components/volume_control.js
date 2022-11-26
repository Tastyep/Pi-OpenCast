import React, { useState } from "react";

import { Stack, Slider, IconButton, Box } from "@mui/material";

import VolumeUpIcon from "@mui/icons-material/VolumeUp";
import VolumeOffIcon from "@mui/icons-material/VolumeOff";
import VolumeDownIcon from "@mui/icons-material/VolumeDown";

import playerAPI from "services/api/player";
import { useAppStore } from "providers/app_context";
import { observer } from "mobx-react-lite";

const VolumeControl = observer((props) => {
  const {
    buttonSize = "medium",
    iconSize = "medium",
    iconColor = "primary",
    sliderColor = "secondary",
    height = 2,
    sx,
  } = props;
  const store = useAppStore();
  const [oldVolume, setOldVolume] = useState(store.player.volume);

  const handleCommit = (_, value) => {
    playerAPI.updateVolume(value);
  };

  const toggleMute = () => {
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
    <Stack direction="row" justifyContent="end" alignItems="center" sx={sx}>
      <IconButton size={buttonSize} color={iconColor} onClick={toggleMute}>
        {(store.player.volume === 0 && (
          <VolumeOffIcon fontSize={iconSize} />
        )) || <VolumeDownIcon fontSize={iconSize} />}
      </IconButton>
      <Box justifyContent="center" sx={{ display: "flex", flex: 1 }}>
        <Slider
          color={sliderColor}
          value={store.player.volume}
          valueLabelDisplay="auto"
          aria-labelledby="continuous-slider"
          sx={{
            height: { height },
            width: "96%",
            marginLeft: "4px",
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
      </Box>
      <IconButton
        size={buttonSize}
        color={iconColor}
        sx={{
          marginLeft: "8px",
        }}
      >
        <VolumeUpIcon fontSize={iconSize} />
      </IconButton>
    </Stack>
  );
});

export { VolumeControl };
