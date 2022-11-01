import { useState } from "react";

import TextField from "@mui/material/TextField";
import Stack from "@mui/material/Stack";
import InputAdornment from "@mui/material/InputAdornment";
import Box from "@mui/material/Box";
import IconButton from "@mui/material/IconButton";

import SearchIcon from "@mui/icons-material/Search";
import ClearIcon from "@mui/icons-material/Clear";

import { observer } from "mobx-react-lite";

import { useMediaQuery } from "react-responsive";
import { SIZES } from "constants.js";

import { filterVideos } from "services/playlist";
import { useAppStore } from "providers/app_context";
import { VirtualizedMediaList } from "components/media_list";

const MediasPage = observer(() => {
  const store = useAppStore();

  const videos = Object.values(store.videos);
  const [input, setInput] = useState("");

  const isSmallDevice = useMediaQuery({
    maxWidth: SIZES.small.max,
  });

  const updateInputContent = (e) => {
    setInput(e.target.value);
  };

  const updateBlur = (evt) => {
    if (evt.key === "Enter") {
      evt.target.blur();
    }
  };

  const endAdornment =
    input.length > 0 ? (
      <InputAdornment position="end">
        <IconButton color="primary" onClick={() => setInput("")}>
          <ClearIcon />
        </IconButton>
      </InputAdornment>
    ) : (
      <InputAdornment position="end">
        <IconButton color="primary">
          <SearchIcon />
        </IconButton>
      </InputAdornment>
    );

  return (
    <Stack direction="column" sx={{ flex: 1 }}>
      <Box
        sx={{
          alignSelf: "end",
          width: isSmallDevice ? "100%" : "fit-content",
          padding: "8px 16px",
          boxSizing: "border-box",
        }}
      >
        <TextField
          fullWidth
          variant="standard"
          label="Filter"
          size="small"
          value={input}
          onChange={updateInputContent}
          onKeyPress={updateBlur}
          InputProps={{
            endAdornment: endAdornment,
          }}
        />
      </Box>
      <VirtualizedMediaList
        videos={filterVideos(store.artists, store.albums, videos, input)}
        style={{ width: "100%", height: "100%", minHeight: "0px" }}
      />
    </Stack>
  );
});

export default MediasPage;
