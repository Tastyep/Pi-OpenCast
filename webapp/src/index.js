import React from "react";
import ReactDOM from "react-dom";
import "./index.css";
import App from "views/app";
import { AppProvider } from "components/app_context";

ReactDOM.render(
  <React.StrictMode>
    <AppProvider>
      <App />
    </AppProvider>
  </React.StrictMode>,
  document.getElementById("root")
);
