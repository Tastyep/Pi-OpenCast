import { deepOrange, grey } from "@mui/material/colors";

const darkTheme = {
  palette: {
    mode: "dark",
    primary: deepOrange,
    divider: deepOrange[200],
    background: {
      default: deepOrange[900],
      paper: deepOrange[900],
    },
    text: {
      primary: grey[50],
      secondary: grey[300],
    },
  },
  typography: {
    body1: {
      color: grey[50],
    },
    body2: {
      color: grey[100],
    },
  },
};

export default darkTheme;
