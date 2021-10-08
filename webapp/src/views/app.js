import React, { useEffect } from "react";

import { Grid } from "@material-ui/core";
import { makeStyles, createStyles } from "@material-ui/core/styles";

import { Tabs, Tab } from "@material-ui/core";
import { BrowserRouter as Router, Switch, Route, Link } from "react-router-dom";

import { observer } from "mobx-react-lite";

import ControlBar from "components/control_bar";
import HomePage from "views/home";
import LibraryPage from "views/library";

import { useAppStore } from "components/app_context";

const useStyles = makeStyles(() =>
  createStyles({
    fullLayout: {
      backgroundColor: "#FFFFFF",
      height: `calc(100vh - 56px)`,
    },
    layout: {
      backgroundColor: "#F5F5F5",
      height: `calc(100vh - (56px + 80px))`,
    },
    columns: {
      backgroundColor: "#F2F2F2",
    },
    pageContainer: {
      height: "100%",
    },
    tabs: {
      backgroundColor: "#888888",
    },
  })
);

const App = observer(() => {
  const store = useAppStore();
  const classes = useStyles();
  const [value, setValue] = React.useState(0);
  const isPlayerActive = store.player && !store.player.isStopped;

  useEffect(() => {
    store.load();
  }, [store]);

  return (
    <Router>
      <Tabs
        value={value}
        onChange={(_, newValue) => {
          setValue(newValue);
        }}
        centered
        className={classes.tabs}
      >
        <Tab label="Home" to="/" component={Link} />
        <Tab label="Library" to="/library" component={Link} />
      </Tabs>
      <Grid
        container
        className={isPlayerActive ? classes.layout : classes.fullLayout}
      >
        <Grid item xs={false} sm={1} className={classes.columns}></Grid>
        <Grid item xs={12} sm={10} className={classes.pageContainer}>
          <Switch>
            <Route exact path="/">
              <HomePage />
            </Route>
            <Route path="/library">
              <LibraryPage />
            </Route>
          </Switch>
        </Grid>
        <Grid item xs={false} sm={1} className={classes.columns}></Grid>
      </Grid>
      {isPlayerActive && <ControlBar />}
    </Router>
  );
});

export default App;
