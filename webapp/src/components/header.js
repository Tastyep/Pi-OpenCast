import React from "react";
import { AppBar, Toolbar, Typography } from "@material-ui/core";
import CastConnectedIcon from "@material-ui/icons/CastConnected";
import { makeStyles } from "@material-ui/styles";

const useStyles = makeStyles(() => ({
  typographyStyles: {
    flex: 1,
  },
}));

const Header = () => {
  const classes = useStyles();
  return (
    <AppBar position="static">
      <Toolbar>
        <Typography className={classes.typographyStyles}>OpenCast</Typography>
        <CastConnectedIcon />
      </Toolbar>
    </AppBar>
  );
};

export default Header;
