import React from "react";
import ReactDOM from "react-dom";

import App from "views/app";
import { AppProvider } from "providers/app_context";
import SnackBarProvider from "providers/snack_bar";
import ThemeProvider from "providers/theme";

import "./index.css";

ReactDOM.render(
  <React.StrictMode>
    <ThemeProvider>
      <AppProvider>
        <SnackBarProvider>
          <App />
        </SnackBarProvider>
      </AppProvider>
    </ThemeProvider>
  </React.StrictMode>,
  document.getElementById("root")
);
