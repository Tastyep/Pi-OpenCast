import React from "react";
import ReactDOM from "react-dom";

import MediaQuery from "react-responsive";
import { SIZES } from "constants.js";

import { SnackbarProvider } from "notistack";

import App from "views/app";
import { AppProvider } from "components/app_context";

import "./index.css";

const SnackBarProviderWrapper = (props) => {
  const { children } = props;

  return (
    <MediaQuery maxWidth={SIZES.small.max}>
      {(matches) =>
        matches ? (
          <SnackbarProvider
            dense
            maxSnack={2}
            anchorOrigin={{
              vertical: "bottom",
              horizontal: "center",
            }}
          >
            {children}
          </SnackbarProvider>
        ) : (
          <SnackbarProvider
            maxSnack={5}
            anchorOrigin={{
              vertical: "top",
              horizontal: "right",
            }}
          >
            {children}
          </SnackbarProvider>
        )
      }
    </MediaQuery>
  );
};

ReactDOM.render(
  <React.StrictMode>
    <AppProvider>
      <SnackBarProviderWrapper>
        <App />
      </SnackBarProviderWrapper>
    </AppProvider>
  </React.StrictMode>,
  document.getElementById("root")
);
