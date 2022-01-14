import React from "react";
import { AppBar, Toolbar, Typography, IconButton } from "@mui/material";
import CastConnectedIcon from "@mui/icons-material/CastConnected";

const Header = () => {
  return (
    <AppBar position="static" elevation={1}>
      <Toolbar>
        <IconButton edge="start" color="inherit" aria-label="menu">
          <CastConnectedIcon />
        </IconButton>
        <Typography variant="h6">OpenCast</Typography>
      </Toolbar>
    </AppBar>
  );
};

export default Header;
