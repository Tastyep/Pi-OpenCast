import React, { useEffect } from "react";

import { Container } from "@material-ui/core";
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
    page: {
      backgroundColor: "#F5F5F5",
      minHeight: "90vh",
      maxHeight: "100vh",
    },
    tabs: {
      backgroundColor: "#C5C5C5",
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
      <Container className={classes.page}>
        <Switch>
          <Route exact path="/">
            <HomePage />
          </Route>
          <Route path="/library">
            <LibraryPage />
          </Route>
        </Switch>
      </Container>
      {store.player && !store.player.isStopped && <ControlBar />}
    </Router>
  );
});

export default App;
