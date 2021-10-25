import { useState } from "react";

import Box from "@mui/material/Box";
import Modal from "@mui/material/Modal";
import Button from "@mui/material/Button";
import TextField from "@mui/material/TextField";
import Typography from "@mui/material/Typography";
import { styled } from "@mui/material/styles";

import { useAppStore } from "components/app_context";
import playlistAPI from "services/api/playlist";
import snackBarHandler from "services/api/error";

const ModalContent = styled(Box)({
  position: "absolute",
  top: "50%",
  left: "50%",
  transform: "translate(-50%, -50%)",
  width: 400,
  maxWidth: "75%",
  backgroundColor: "#FFFFFF",
  border: "2px solid #000",
  boxShadow: 24,

  p: 4,
  padding: "16px",
});

const PlaylistModal = (props) => {
  const store = useAppStore();

  const [title, setTitle] = useState("");
  const { open, close, videos = [] } = props;

  const createPlaylist = () => {
    const ids = videos.map((video) => video.id);
    playlistAPI
      .create({ name: title, ids: ids })
      .then((_) => {
        store.enqueueSnackbar({
          message: "playlist '" + title + "' created",
          options: {
            variant: "success",
          },
        });
      })
      .catch(snackBarHandler(store));
    close();
  };

  return (
    <Modal open={open} onClose={close}>
      <ModalContent>
        <Typography variant="h6" sx={{ marginBottom: "8px" }}>
          New playlist
        </Typography>
        <TextField
          id="standard-basic"
          label="Title"
          variant="standard"
          autoFocus
          sx={{ width: "100%" }}
          onChange={(e) => setTitle(e.target.value)}
        />
        <div
          style={{
            display: "flex",
            justifyContent: "end",
            marginTop: "24px",
          }}
        >
          <Button variant="text" onClick={close}>
            Cancel
          </Button>
          <Button variant="contained" onClick={() => createPlaylist()}>
            Save
          </Button>
        </div>
      </ModalContent>
    </Modal>
  );
};

export default PlaylistModal;
