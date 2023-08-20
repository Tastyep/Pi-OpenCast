import React, { useState } from "react";

import AppBar from "@mui/material/AppBar";
import Drawer from "@mui/material/Drawer";
import Grid from "@mui/material/Grid";
import Tabs from "@mui/material/Tabs";
import Tab from "@mui/material/Tab";
import Box from "@mui/material/Box";
import Stack from "@mui/material/Stack";
import Collapse from "@mui/material/Collapse";
import Toolbar from "@mui/material/Toolbar";
import Typography from "@mui/material/Typography";

import { useTheme } from "@mui/material/styles";

import OndemandVideoIcon from "@mui/icons-material/OndemandVideo";
import FavoriteIcon from "@mui/icons-material/Favorite";
import PlaylistPlayIcon from "@mui/icons-material/PlaylistPlay";
import GroupsIcon from "@mui/icons-material/Groups";
import AlbumIcon from "@mui/icons-material/Album";
import SearchIcon from "@mui/icons-material/Search";

import OpenCastIcon from "assets/icon.svg";

import {
  BrowserRouter as Router,
  Routes,
  Route,
  Link,
  Outlet,
  useLocation,
} from "react-router-dom";

import { observer } from "mobx-react-lite";

import { useMediaQuery } from "react-responsive";
import { SIZES } from "constants.js";

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

import ControlBar from "components/control_bar";
import PlayerProgress from "components/player_progress";
import Notifier from "components/notifier";
import StreamInput from "components/stream_input";

import { hexToRgba } from "services/color";

import { useAppStore } from "providers/app_context";

const MobileHeaderTabs = (props) => {
  const { sx } = props;

  const location = useLocation();

  let rootURL = location.pathname;
  const secondSlashPos = rootURL.indexOf("/", 1);
  if (secondSlashPos !== -1) {
    rootURL = rootURL.substring(0, secondSlashPos);
  }

  return (
    <Tabs
      allowScrollButtonsMobile
      scrollButtons="auto"
      variant="scrollable"
      value={rootURL}
      textColor="inherit"
      indicatorColor="secondary"
      sx={sx}
    >
      <Tab value="/" to="/" icon={<OndemandVideoIcon />} component={Link} />
      <Tab
        value="/profile"
        to="/profile"
        icon={<FavoriteIcon />}
        component={Link}
      />
      <Tab
        value={"/playlists"}
        to={"playlists"}
        icon={<PlaylistPlayIcon />}
        component={Link}
      />
      <Tab
        value={"/artists"}
        to={"artists"}
        icon={<GroupsIcon />}
        component={Link}
      />
      <Tab
        value={"/albums"}
        to={"albums"}
        icon={<AlbumIcon />}
        component={Link}
      />
      <Tab
        value={"/medias"}
        to={"medias"}
        icon={<SearchIcon />}
        component={Link}
      />
    </Tabs>
  );
};

const DesktopHeaderTabs = (props) => {
  const { sx } = props;

  const location = useLocation();

  let rootURL = location.pathname;
  const secondSlashPos = rootURL.indexOf("/", 1);
  if (secondSlashPos !== -1) {
    rootURL = rootURL.substring(0, secondSlashPos);
  }

  const tabSx = {
    justifyContent: "flex-start",
    minHeight: "56px",

    "& .MuiTab-iconWrapper": {
      width: "24px",
      height: "24px",
      marginRight: "12px",
    },
  };

  return (
    <Tabs
      variant="standard"
      value={rootURL}
      textColor="inherit"
      orientation="vertical"
      sx={sx}
    >
      <Tab
        label="Player"
        value="/"
        to="/"
        disableRipple={true}
        iconPosition="start"
        icon={<OndemandVideoIcon />}
        component={Link}
        sx={tabSx}
      />
      <Tab
        label="Profile"
        value="/profile"
        to="/profile"
        disableRipple={true}
        iconPosition="start"
        icon={<FavoriteIcon />}
        component={Link}
        sx={tabSx}
      />
      <Tab
        label="Playlists"
        value={"/playlists"}
        to={"playlists"}
        disableRipple={true}
        iconPosition="start"
        icon={<PlaylistPlayIcon />}
        component={Link}
        sx={tabSx}
      />
      <Tab
        label="Artists"
        value={"/artists"}
        to={"artists"}
        disableRipple={true}
        iconPosition="start"
        icon={<GroupsIcon />}
        component={Link}
        sx={tabSx}
      />
      <Tab
        label="Albums"
        value={"/albums"}
        to={"albums"}
        disableRipple={true}
        iconPosition="start"
        icon={<AlbumIcon />}
        component={Link}
        sx={tabSx}
      />
      <Tab
        label="Medias"
        value={"/medias"}
        to={"medias"}
        disableRipple={true}
        iconPosition="start"
        icon={<SearchIcon />}
        component={Link}
        sx={tabSx}
      />
    </Tabs>
  );
};

const MobileHeader = (props) => {
  const theme = useTheme();

  return (
    <AppBar
      position="sticky"
      sx={{
        backgroundColor: theme.palette.primary.dark,
      }}
    >
      <Box sx={{ paddingTop: "12px" }}>
        <StreamInput />
        <MobileHeaderTabs />
      </Box>
    </AppBar>
  );
};

const DesktopHeader = () => {
  const theme = useTheme();

  return (
    <AppBar
      position="sticky"
      sx={{
        backgroundColor: theme.palette.primary.dark,
        zIndex: (theme) => theme.zIndex.drawer + 1,
      }}
    >
      <Grid
        container
        sx={{
          padding: "8px 16px 6px 16px",
        }}
      >
        <Grid item xs={3} />
        <Grid item xs>
          <StreamInput />
        </Grid>
        <Grid item xs={3} />
      </Grid>
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

const SmallLayout = () => {
  const [controlPageOpen, setControlPageOpenState] = useState(false);

  return (
    <Stack sx={{ height: "100%" }}>
      <Notifier />
      {controlPageOpen ? (
        <ControlPage closePage={() => setControlPageOpenState(false)} />
      ) : (
        <>
          <MobileHeader controlPageOpen={controlPageOpen} />
          <Box
            sx={{
              display: "flex",
              flex: 1,
              minHeight: "0px",
              margin: "0px 8px 0px 8px",
            }}
          >
            <Outlet />
          </Box>
          <CollapsableControlBar
            openTrackInfo={() => setControlPageOpenState(true)}
          />
        </>
      )}
    </Stack>
  );
};

const LargeLayout = () => {
  const navWidth = "360px";

  const theme = useTheme();
  const navIndicatorColor = hexToRgba(theme.palette.primary.main, 0.5);

  return (
    <Stack sx={{ height: "100%" }}>
      <Notifier />
      <DesktopHeader />
      <Stack direction="row" sx={{ flex: 1 }}>
        <Drawer
          variant="permanent"
          sx={{
            width: navWidth,
            flexShrink: 0,
          }}
          PaperProps={{
            sx: {
              width: navWidth,
              boxSizing: "border-box",
            },
          }}
        >
          <Toolbar />
          <Stack
            direction="row"
            sx={{ alignItems: "flex-end", padding: "16px 24px 32px 16px" }}
          >
            <img
              src={OpenCastIcon}
              style={{ width: "48px", height: "48px", margin: "0px 16px" }}
            />
            <Typography
              variant="h5"
              sx={{
                display: "flex",
                alignItems: "center",
              }}
            >
              OpenCast
            </Typography>
          </Stack>
          <DesktopHeaderTabs
            smallLayout={false}
            sx={{
              marginLeft: "12px",
              marginRight: "12px",
              "& .MuiTabs-indicator": {
                width: "100%",
                borderRadius: "32px",
                backgroundColor: navIndicatorColor,
              },
            }}
          />
        </Drawer>
        <Box
          sx={{
            display: "flex",
            flex: 1,
            margin: "0px 32px",
            overflow: "auto",
          }}
        >
          <Outlet />
        </Box>
      </Stack>
    </Stack>
  );
};

const App = () => {
  const isSmallDevice = useMediaQuery({
    maxWidth: SIZES.small.max,
  });

  return (
    <Router>
      <Routes>
        <Route
          path="/"
          element={isSmallDevice ? <SmallLayout /> : <LargeLayout />}
        >
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
