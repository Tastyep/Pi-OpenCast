import React, { useEffect } from "react";

import { Divider, Grid, Tabs, Tab } from "@mui/material";
import { styled } from "@mui/material/styles";

import { BrowserRouter as Router, Switch, Route, Link } from "react-router-dom";

import { observer } from "mobx-react-lite";

import ControlBar from "components/control_bar";
import HomePage from "views/home";
import LibraryPage from "views/library";

import { useAppStore } from "components/app_context";

const StyledTab = styled((props) => <Tab {...props} />)(() => ({
  color: "#B0B0B0",
  "&.Mui-selected": {
    color: "#FFFFFF",
    backgroundColor: "#111111",
  },
}));

const App = observer(() => {
  const store = useAppStore();

  const [value, setValue] = React.useState(0);
  const isPlayerActive = store.player && !store.player.isStopped;

  useEffect(() => {
    store.load();
  }, [store]);

  return (
    <Router style={{ height: "100vh" }}>
      <Tabs
        value={value}
        onChange={(_, newValue) => {
          setValue(newValue);
        }}
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
        <StyledTab label="Home" to="/" component={Link} />
        <Divider
          ortientation="vertical"
          sx={{ backgroundColor: "#000000", width: "1px" }}
        />
        <StyledTab label="Library" to="/library" component={Link} />
        <Divider
          ortientation="vertical"
          sx={{ backgroundColor: "#000000", width: "1px" }}
        />
      </Tabs>
      <Grid
        container
        sx={{
          height: isPlayerActive
            ? `calc(100vh - (2 * 48px))`
            : `calc(100vh - 48px)`,
        }}
      >
        <Grid item xs={false} sm={1} sx={{ backgroundColor: "#F2F2F2" }}></Grid>
        <Grid item xs={12} sm={10} sx={{ height: "100%" }}>
          <Switch>
            <Route exact path="/">
              <HomePage />
            </Route>
            <Route path="/library">
              <LibraryPage />
            </Route>
          </Switch>
        </Grid>
        <Grid item xs={false} sm={1} sx={{ backgroundColor: "#F2F2F2" }}></Grid>
      </Grid>
      {isPlayerActive && <ControlBar />}
    </Router>
  );
});

export default App;
