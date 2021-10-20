import React, { useState } from "react";

import { TextField, Button, Stack } from "@mui/material";
import PlayArrowIcon from "@mui/icons-material/PlayArrow";
import AddToQueueIcon from "@mui/icons-material/AddToQueue";

import playerAPI from "services/api/player";
import snackBarHandler from "services/api/error";

import { useAppStore } from "components/app_context";

const StreamInput = () => {
  const store = useAppStore();

  const [url, setUrl] = useState("");
  const [cast, setCast] = useState(true);
  const [action, setAction] = useState(() => playerAPI.streamMedia);

  const handleSubmit = (event) => {
    if (event) {
      event.preventDefault();
    }
    if (url === "") {
      return;
    }
    action(url).catch(snackBarHandler(store));
    setUrl("");
  };

  const handleActionChange = () => {
    setCast(!cast);
    setAction(cast ? () => playerAPI.streamMedia : () => playerAPI.queueMedia);
  };

  return (
    <form onSubmit={(e) => handleSubmit(e)} noValidate autoComplete="off">
      <Stack direction="row">
        <TextField
          fullWidth
          label="Media's URL"
          value={url}
          onChange={(e) => setUrl(e.target.value)}
        />
        <Button
          value="check"
          size="medium"
          variant="outlined"
          selected={cast}
          sx={{ marginLeft: "24px", color: "#333333", borderColor: "#8F8F8F" }}
          onClick={handleActionChange}
        >
          {cast ? <PlayArrowIcon /> : <AddToQueueIcon />}
        </Button>
      </Stack>
    </form>
  );
};

export default StreamInput;
