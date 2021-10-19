import React, { useEffect } from "react";

import { Divider, Grid, Tabs, Tab } from "@mui/material";
import { styled } from "@mui/material/styles";

import {
  BrowserRouter as Router,
  Switch,
  Route,
  Link,
  useLocation,
} from "react-router-dom";

import { observer } from "mobx-react-lite";

import ControlBar from "components/control_bar";
import Notifier from "components/notifier";
import HomePage from "views/home";
import LibraryPage from "views/library";
import PlaylistPage from "views/playlist";
import AlbumPage from "views/album";

import { useAppStore } from "components/app_context";

const StyledTab = styled((props) => <Tab {...props} />)(() => ({
  color: "#B0B0B0",
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
      <Divider
        ortientation="vertical"
        sx={{ backgroundColor: "#000000", width: "1px" }}
      />
      <StyledTab label="Home" value="/" to="/" component={Link} />
      <Divider
        ortientation="vertical"
        sx={{ backgroundColor: "#000000", width: "1px" }}
      />
      <StyledTab
        label="Library"
        value="/library"
        to="/library"
        component={Link}
      />
      <Divider
        ortientation="vertical"
        sx={{ backgroundColor: "#000000", width: "1px" }}
      />
    </Tabs>
  );
};

const App = observer(() => {
  const store = useAppStore();
  const isPlayerActive = store.player && !store.player.isStopped;

  useEffect(() => {
    store.load();
  }, [store]);

  return (
    <div style={{ display: "flex", flexDirection: "column", height: "100vh" }}>
      <Notifier />
      <Router>
        <HeaderTabs />
        <Grid
          container
          sx={{
            minHeight: "0px", // Set minHeight of flex item to 0 otherwise it defaults to the content's height
            flexGrow: 1,
          }}
        >
          <Grid
            item
            xs={false}
            sm={1}
            sx={{ backgroundColor: "#F2F2F2" }}
          ></Grid>
          <Grid item xs={12} sm={10} sx={{ height: "100%" }}>
            <Switch>
              <Route exact path="/">
                <HomePage />
              </Route>
              <Route path="/library">
                <LibraryPage />
              </Route>
              <Route path="/playlists/:id">
                <PlaylistPage />
              </Route>
              <Route path="/albums/:name">
                <AlbumPage />
              </Route>
            </Switch>
          </Grid>
          <Grid
            item
            xs={false}
            sm={1}
            sx={{ backgroundColor: "#F2F2F2" }}
          ></Grid>
        </Grid>
        {isPlayerActive && (
          <>
            <Divider sx={{ borderColor: "#CECECE" }} />
            <ControlBar />
          </>
        )}
      </Router>
    </div>
  );
});

export default App;
