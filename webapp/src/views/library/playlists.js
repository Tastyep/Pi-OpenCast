import {} from "@mui/material";

import { observer } from "mobx-react-lite";

import { useAppStore } from "components/app_context";

const PlaylistsPage = observer(() => {
  const store = useAppStore();

  return <>{"Playlists"}</>;
});

export default PlaylistsPage;
