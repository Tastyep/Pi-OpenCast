import { grey } from "@mui/material/colors";

const purpleOrangeTheme = {
  palette: {
    mode: "light",
    primary: {
      main: "#901a34",
      light: "#c54e5d",
      dark: "#5c000e",
    },
    // primary: {
    //   main: "#e5975f",
    //   light: "#ffc88d",
    //   dark: "#af6933",
    // },
    // secondary: {
    //   main: "#1a9076",
    //   light: "#57c1a5",
    //   dark: "#00624a",
    // },
    // secondary: {
    //   main: "#b89b1c",
    //   light: "#edca51",
    //   dark: "#836c00",
    // },
    secondary: {
      main: "#00827c",
      light: "#4cb2ab",
      dark: "#005550",
    },
    // secondary: {
    //   main: "#ef8e94",
    //   light: "#ffbfc4",
    //   dark: "#ba5f66",
    // },

    neutral: {
      contrastText: "#FFFFFF",
    },
    action: {
      hover: "rgba(144, 26, 52, 0.04)",
    },

    divider: "#901a34",

    text: {
      primary: grey[900],
      secondary: grey[800],
    },
  },
  typography: {
    body1: {
      color: grey[900],
    },
    body2: {
      color: grey[700],
    },
  },
};

export default purpleOrangeTheme;
