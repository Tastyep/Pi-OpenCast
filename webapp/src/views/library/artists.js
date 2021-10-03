import {} from "@material-ui/core";

import { observer } from "mobx-react-lite";

import { useAppStore } from "components/app_context";

const ArtistsPage = observer(() => {
  const store = useAppStore();

  return <>{"Artists"}</>;
});

export default ArtistsPage;
