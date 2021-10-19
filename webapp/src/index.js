import React from "react";
import ReactDOM from "react-dom";

import { SnackbarProvider } from "notistack";

import App from "views/app";
import { AppProvider } from "components/app_context";

import "./index.css";

ReactDOM.render(
  <React.StrictMode>
    <AppProvider>
      <SnackbarProvider
        maxSnack={3}
        anchorOrigin={{
          vertical: "top",
          horizontal: "right",
        }}
      >
        <App />
      </SnackbarProvider>
    </AppProvider>
  </React.StrictMode>,
  document.getElementById("root")
);
