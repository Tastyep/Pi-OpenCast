import { observer } from "mobx-react-lite";

import { Typography } from "@material-ui/core";

import { useAppStore } from "components/app_context";
import VideoList from "components/video_list";

const LibraryPage = observer(() => {
  const store = useAppStore();

  const listLastPlayedVideos = () => {
    const videos = Object.values(store.videos)
      .sort((a, b) => {
        return new Date(a.last_play) < new Date(b.last_play);
      })
      .slice(0, 5);
    console.log("IT", videos);
    return videos;
  };

  const listPopularVideos = () => {
    const videos = Object.values(store.videos)
      .sort((a, b) => {
        return a.total_playing_duration < b.total_playing_duration;
      })
      .slice(0, 5);
    console.log("IT", videos);
    return videos;
  };

  return (
    <>
      <Typography variant="h6">Recent activity</Typography>
      <VideoList videos={listLastPlayedVideos()} />
      <Typography variant="h6">Most played</Typography>
      <VideoList videos={listPopularVideos()} />
    </>
  );
});

export default LibraryPage;
