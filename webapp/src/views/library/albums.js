import {} from "@mui/material";

import { observer } from "mobx-react-lite";

import { useAppStore } from "components/app_context";

const AlbumsPage = observer(() => {
  const store = useAppStore();

  return <>{"Albums"}</>;
});

export default AlbumsPage;
