import React, { useEffect } from "react";

import { Grid, Paper } from "@material-ui/core";
import { makeStyles, createStyles } from "@material-ui/core/styles";

import { Tabs, Tab } from "@material-ui/core";
import { BrowserRouter as Router, Switch, Route, Link } from "react-router-dom";

import { observer } from "mobx-react-lite";

import ControlBar from "components/control_bar";
import HomePage from "views/home";
import LibraryPage from "views/library";

import Header from "components/header";
import VolumeControl from "components/volume_control";
import { useAppStore } from "components/app_context";

const useStyles = makeStyles(() =>
  createStyles({
    root: {
      width: "100%",
      backgroundColor: "#F5F5F5",
    },
  })
);

const App = observer(() => {
  const store = useAppStore();
  const classes = useStyles();

  useEffect(() => {
    store.load();
  }, [store]);

  const [value, setValue] = React.useState(0);

  const handleChange = (event, newValue) => {
    console.log(event);
    setValue(newValue);
  };
  return (
    <Grid container className={classes.root}>
      <Grid item sm={1} md={2} />
      <Grid item xs={12} sm={10} md={8}>
        <Paper elevation={3} style={{ flex: 1, padding: 24 }}>
          <Router>
            <Tabs value={value} onChange={handleChange} centered>
              <Tab label="Accueil" to="/" component={Link} />
              <Tab label="Bibliotheque" to="/library" component={Link} />
            </Tabs>
            <Switch>
              <Route exact path="/">
                <HomePage />
              </Route>
              <Route path="/library">
                <LibraryPage />
              </Route>
            </Switch>
            {store.player && !store.player.isStopped && <ControlBar />}
          </Router>
        </Paper>
      </Grid>
      <Grid item sm={1} md={2} />
    </Grid>
  );
});

export default App;
