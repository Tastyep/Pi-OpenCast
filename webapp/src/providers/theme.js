import React from "react";

import {
  ThemeProvider as MuiThemeProvider,
  createTheme,
  responsiveFontSizes,
} from "@mui/material";

import darkTheme from "themes/dark/dark";
import purpleOrangeTheme from "themes/light/purple_orange";

const getThemeSpec = (mode) => {
  return mode === "light" ? purpleOrangeTheme : darkTheme;
};

const ThemeProvider = (props) => {
  const { children } = props;

  const [mode, setMode] = React.useState("light");
  // const colorMode = React.useMemo(
  //   () => ({
  //     // The dark mode switch would invoke this method
  //     toggleColorMode: () => {
  //       setMode((prevMode) =>
  //         prevMode === 'light' ? 'dark' : 'light',
  //       );
  //     },
  //   }),
  //   [],
  // );

  // Update the theme only if the mode changes
  const theme = React.useMemo(
    () => responsiveFontSizes(createTheme(getThemeSpec(mode))),
    [mode]
  );

  return <MuiThemeProvider theme={theme}>{children}</MuiThemeProvider>;
};

export default ThemeProvider;
