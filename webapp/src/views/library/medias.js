import { observer } from "mobx-react-lite";

import { useAppStore } from "components/app_context";
import MediaList from "components/media_list";

const MediasPage = observer(() => {
  const store = useAppStore();

  return (
    <div style={{ height: "100%", width: "100%" }}>
      <MediaList medias={Object.values(store.videos)} />
    </div>
  );
});

export default MediasPage;
