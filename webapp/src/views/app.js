import React, { useEffect } from "react";

import { Divider, Grid, Tabs, Tab } from "@mui/material";
import Box from "@mui/material/Box";
import Collapse from "@mui/material/Collapse";
import { styled } from "@mui/material/styles";

import {
  BrowserRouter as Router,
  Routes,
  Route,
  Link,
  Outlet,
  useLocation,
} from "react-router-dom";

import { observer } from "mobx-react-lite";

import ControlBar from "components/control_bar";
import PlayerProgress from "components/player_progress";
import Notifier from "components/notifier";
import HomePage from "views/home";

import {
  LibraryLayout,
  LibraryPage,
  PlaylistsPage,
  ArtistsPage,
  AlbumsPage,
  MediasPage,
} from "views/library";
import PlaylistPage from "views/library/playlist";
import ArtistPage from "views/library/artist";
import AlbumPage from "views/library/album";

import { useAppStore } from "components/app_context";

const StyledTab = styled((props) => <Tab {...props} />)(() => ({
  color: "#B0B0B0",
  border: "black",
  borderStyle: "hidden solid hidden solid",
  borderWidth: "1px",
  "&.Mui-selected": {
    color: "#FFFFFF",
    backgroundColor: "#111111",
  },
}));

const HeaderTabs = () => {
  const location = useLocation();
  let rootURL = location.pathname;
  const secondSlashPos = rootURL.indexOf("/", 1);

  if (secondSlashPos !== -1) {
    rootURL = rootURL.substring(0, secondSlashPos);
  }

  return (
    <Tabs
      value={rootURL}
      TabIndicatorProps={{
        style: {
          display: "none",
        },
      }}
      centered
      sx={{ backgroundColor: "#333333" }}
    >
      <StyledTab label="Home" value="/" to="/" component={Link} />
      <StyledTab
        label="Library"
        value="/library"
        to="/library"
        component={Link}
      />
    </Tabs>
  );
};

const CollapsableControlBar = observer(() => {
  const store = useAppStore();

  if (store.player.isStopped === undefined) {
    return null;
  }

  return (
    <Box>
      <Collapse in={!store.player.isStopped} timeout="auto">
        <PlayerProgress />
        <ControlBar />
      </Collapse>
    </Box>
  );
});

const Layout = () => {
  return (
    <div style={{ display: "flex", flexDirection: "column", height: "100%" }}>
      <Notifier />
      <HeaderTabs />
      <Grid
        container
        sx={{
          minHeight: "0px", // Set minHeight of flex item to 0 otherwise it defaults to the content's height
          flex: 1,
        }}
      >
        <Grid item xs={false} sm={1} sx={{ backgroundColor: "#F2F2F2" }} />
        <Grid item xs={12} sm={10} sx={{ height: "100%" }}>
          <Outlet />
        </Grid>
        <Grid item xs={false} sm={1} sx={{ backgroundColor: "#F2F2F2" }} />
      </Grid>
      <CollapsableControlBar />
    </div>
  );
};

const App = () => {
  const store = useAppStore();

  useEffect(() => {
    store.load();
  }, [store]);

  console.log("APP");

  return (
    <Router>
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<HomePage />} />
          <Route path="library" element={<LibraryLayout />}>
            <Route index element={<LibraryPage />} />
            <Route path={"playlists"} element={<PlaylistsPage />} />
            <Route path={"artists"} element={<ArtistsPage />} />
            <Route path={"albums"} element={<AlbumsPage />} />
            <Route path={"medias"} element={<MediasPage />} />
            <Route path={"playlists/:id"} element={<PlaylistPage />} />
            <Route path={"artists/:name"} element={<ArtistPage />} />
            <Route path={"albums/:name"} element={<AlbumPage />} />
          </Route>
        </Route>
      </Routes>
    </Router>
  );
};

export default App;
