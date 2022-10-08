import { grey } from "@mui/material/colors";

const purpleOrangeTheme = {
  palette: {
    mode: "light",
    primary: {
      main: "#901a34",
      light: "#c54e5d",
      dark: "#5c000e",
    },
    // secondary: {
    //   main: "#1a9076",
    //   light: "#57c1a5",
    //   dark: "#00624a",
    // },
    secondary: {
      main: "#b89b1c",
      light: "#edca51",
      dark: "#836c00",
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
