import { useState } from "react";

import { Box, Button, Divider, List, Stack, Typography } from "@mui/material";
import Modal from "@mui/material/Modal";
import TextField from "@mui/material/TextField";
import EditIcon from "@mui/icons-material/Edit";
import { styled } from "@mui/material/styles";

import { useParams } from "react-router-dom";

import { observer } from "mobx-react-lite";

import { useAppStore } from "components/app_context";
import PlaylistThumbnail from "components/playlist_thumbnail";
import MediaItem from "components/media_item";

import playlistAPI from "services/api/playlist";

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

const UpdateModal = (props) => {
  const store = useAppStore();

  const { open, close, playlist } = props;
  const [name, setName] = useState(playlist.name);

  const updatePlaylist = () => {
    playlistAPI.update(playlist.id, { name: name }).catch((error) =>
      store.enqueueSnackbar({
        message: error.response.data.message,
        options: {
          variant: "error",
        },
      })
    );
    close();
  };

  return (
    <Modal open={open} onClose={close}>
      <ModalContent>
        <Typography variant="h6" sx={{ marginBottom: "8px" }}>
          {playlist.name}
        </Typography>
        <TextField
          id="standard-basic"
          label="Title"
          variant="standard"
          defaultValue={playlist.name}
          autoFocus
          sx={{ width: "100%" }}
          onChange={(e) => setName(e.target.value)}
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
          <Button variant="contained" onClick={() => updatePlaylist()}>
            Save
          </Button>
        </div>
      </ModalContent>
    </Modal>
  );
};

const PlaylistPage = observer(() => {
  const store = useAppStore();
  const { id } = useParams();

  const [isModalOpen, setModalOpen] = useState(false);

  const playlist = store.playlists[id];
  const videos = store.playlistVideos(id);

  if (!playlist) {
    return null;
  }

  return (
    <Box sx={{ display: "flex", flexDirection: "column", height: "100%" }}>
      <UpdateModal
        open={isModalOpen}
        close={() => setModalOpen(false)}
        playlist={playlist}
      />
      <Box
        sx={{
          display: "flex",
          flexDirection: "row",
          alignItems: "center",
          marginTop: "32px",
          marginBottom: "32px",
          marginLeft: "16px",
        }}
      >
        <Box sx={{ marginRight: "32px", height: 128, width: 128 }}>
          <PlaylistThumbnail videos={videos} />
        </Box>
        <Box>
          <Typography variant="h4">{playlist.name}</Typography>
          <Typography>{videos.length} medias</Typography>
          <Stack direction="row" sx={{ marginTop: "16px" }}>
            <Button
              variant="outlined"
              startIcon={<EditIcon />}
              sx={{ alignItems: "flex-start" }}
              onClick={() => setModalOpen(true)}
            >
              Edit playlist
            </Button>
          </Stack>
        </Box>
      </Box>
      <Divider />
      <Box
        sx={{
          height: "100%",
          width: "100%",
          overflow: "auto",
        }}
      >
        <List sx={{ height: "100%", width: "100%", padding: "0px" }}>
          {videos.map((video) => (
            <MediaItem key={video.id} playlist={playlist} video={video} />
          ))}
        </List>
      </Box>
    </Box>
  );
});

export default PlaylistPage;
