import React, { useState } from "react";

import AppBar from "@mui/material/AppBar";
import Drawer from "@mui/material/Drawer";
import Grid from "@mui/material/Grid";
import Tabs from "@mui/material/Tabs";
import Tab from "@mui/material/Tab";
import Box from "@mui/material/Box";
import Stack from "@mui/material/Stack";
import Collapse from "@mui/material/Collapse";
import { styled, useTheme } from "@mui/material/styles";

import {
  BrowserRouter as Router,
  Routes,
  Route,
  Link,
  Outlet,
  useLocation,
} from "react-router-dom";

import { observer } from "mobx-react-lite";

import MediaQuery from "react-responsive";
import { SIZES } from "constants.js";

import ControlBar from "components/control_bar";
import PlayerProgress from "components/player_progress";
import Notifier from "components/notifier";
import HomePage from "views/home";
import ControlPage from "views/control";

import ProfilePage from "views/profile";
import AlbumsPage from "views/library/albums";
import AlbumPage from "views/library/album";
import ArtistsPage from "views/library/artists";
import ArtistPage from "views/library/artist";
import MediasPage from "views/library/medias";
import PlaylistsPage from "views/library/playlists";
import PlaylistPage from "views/library/playlist";

import StreamInput from "components/stream_input";

import { useAppStore } from "providers/app_context";

const HeaderTabs = (props) => {
  const { sx } = props;

  const location = useLocation();

  let rootURL = location.pathname;
  const secondSlashPos = rootURL.indexOf("/", 1);
  if (secondSlashPos !== -1) {
    rootURL = rootURL.substring(0, secondSlashPos);
  }

  return (
    <Box display="flex" justifyContent="center" sx={{ width: "100%" }}>
      <Tabs
        allowScrollButtonsMobile
        scrollButtons="auto"
        variant="scrollable"
        value={rootURL}
        textColor="inherit"
        TabIndicatorProps={{
          style: {
            display: "none",
          },
        }}
        sx={sx}
      >
        <Tab label="Player" value="/" to="/" component={Link} />
        <Tab label="Profile" value="/profile" to="/profile" component={Link} />
        <Tab
          label="Playlists"
          value={"/playlists"}
          to={"playlists"}
          component={Link}
        />
        <Tab
          label="Artists"
          value={"/artists"}
          to={"artists"}
          component={Link}
        />
        <Tab label="Albums" value={"/albums"} to={"albums"} component={Link} />
        <Tab label="Titles" value={"/medias"} to={"medias"} component={Link} />
      </Tabs>
    </Box>
  );
};

const Header = () => {
  const theme = useTheme();

  return (
    <AppBar
      position="sticky"
      sx={{
        backgroundColor: theme.palette.primary.main,
      }}
    >
      <MediaQuery minWidth={SIZES.xlarge.min}>
        {(matches) =>
          matches ? (
            <Grid
              container
              sx={{
                padding: "8px 16px 4px 16px",
              }}
            >
              <Grid item xs={3} sx={{ marginTop: "2px" }}>
                <StreamInput />
              </Grid>
              <Grid item xs>
                <HeaderTabs />
              </Grid>
              <Grid item xs={3} />
            </Grid>
          ) : (
            <Box sx={{ paddingTop: "12px" }}>
              <StreamInput />
              <HeaderTabs />
            </Box>
          )
        }
      </MediaQuery>
    </AppBar>
  );
};

const CollapsableControlBar = observer((props) => {
  const store = useAppStore();
  const { openTrackInfo } = props;

  if (store.player.isStopped === undefined) {
    return null;
  }

  return (
    <Box>
      <Collapse in={!store.player.isStopped} timeout="auto">
        <PlayerProgress />
        <ControlBar openTrackInfo={openTrackInfo} />
      </Collapse>
    </Box>
  );
});

const Layout = () => {
  const [controlPageOpen, closeControlPage] = useState(false);

  return (
    <Stack sx={{ height: "100%" }}>
      <Notifier />
      <Header />
      <Grid
        container
        sx={{
          minHeight: "0px", // Set minHeight of flex item to 0 otherwise it defaults to the content's height
          flex: 1,
        }}
      >
        <Grid item xs={false} sm={1} sx={{ backgroundColor: "#F2F2F2" }} />
        <Grid
          item
          container
          xs={12}
          sm={10}
          sx={{ height: "100%", overflow: "auto" }}
        >
          <Drawer
            anchor="top"
            open={controlPageOpen}
            onClose={() => closeControlPage(false)}
          >
            <ControlPage closePage={() => closeControlPage(false)} />
          </Drawer>
          <Outlet />
        </Grid>
        <Grid item xs={false} sm={1} sx={{ backgroundColor: "#F2F2F2" }} />
      </Grid>
      {!controlPageOpen && (
        <CollapsableControlBar openTrackInfo={() => closeControlPage(true)} />
      )}
    </Stack>
  );
};

const App = () => {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<HomePage />} />
          <Route path={"profile"} element={<ProfilePage />} />
          <Route path={"playlists"} element={<PlaylistsPage />} />
          <Route path={"artists"} element={<ArtistsPage />} />
          <Route path={"albums"} element={<AlbumsPage />} />
          <Route path={"medias"} element={<MediasPage />} />
          <Route path={"playlists/:id"} element={<PlaylistPage />} />
          <Route path={"artists/:id"} element={<ArtistPage />} />
          <Route path={"albums/:id"} element={<AlbumPage />} />
        </Route>
      </Routes>
    </Router>
  );
};

export default App;
