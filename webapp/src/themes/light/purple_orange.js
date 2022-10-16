import { grey } from "@mui/material/colors";
import { mixColor } from "services/color";

const primary = {
  main: "#232F34",
  light: "#47606A",
  dark: "#1B2529",
};

// const primary = {
//   main: "#7d9365",
//   light: "#adc393",
//   dark: "#50653a",
// };

const purpleOrangeTheme = {
  palette: {
    mode: "light",
    primary: primary,
    // primary: {
    //   main: "#901a34",
    //   light: "#c54e5d",
    //   dark: "#5c000e",
    // },
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
    // secondary: {
    //   main: "#00827c",
    //   light: "#4cb2ab",
    //   dark: "#005550",
    // },
    // secondary: {
    //   main: "#ef8e94",
    //   light: "#ffbfc4",
    //   dark: "#ba5f66",
    // },

    // secondary: {
    //   main: "#903b1a",
    //   light: "#c56843",
    //   dark: "#5d0d00",
    // },

    // secondary: {
    //   main: "#7a6593",
    //   light: "#aa93c4",
    //   dark: "#4d3a65",
    // },

    secondary: {
      main: "#F9AA33",
      light: "#F9B043",
      dark: "#D08006",
    },

    error: {
      main: "#BB3E4B",
      light: "#CC6670",
      dark: "#6B242B",
    },

    warning: {
      main: "#BBAF3E",
      light: "#CCC266",
      dark: "#504B1B",
    },

    info: {
      main: "#7e91a0",
      light: "#9AA9B4",
      dark: "#4E5E6A",
    },

    success: {
      main: primary.light,
      light: "#BED565",
      dark: "#647520",
    },

    neutral: {
      light: "#FFFFFF",
    },
    action: {
      hover: mixColor(primary.light, "#11FFFFFF", 0.9),
    },

    divider: primary.main,

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
