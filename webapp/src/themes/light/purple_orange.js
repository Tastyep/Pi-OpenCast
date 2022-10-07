import { grey } from "@mui/material/colors";

const purpleOrangeTheme = {
  palette: {
    mode: "light",
    primary: {
      main: "#f9a825",
      light: "#ffd95a",
      dark: "#c17900",
    },
    secondary: {
      main: "#8e24aa",
      light: "#c158dc",
      dark: "#5c007a",
    },
    divider: grey[300],
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
