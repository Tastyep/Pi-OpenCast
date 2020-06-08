import React, { Component } from "react";

import "./app.css";
import StreamInput from "./stream_input.js";

class App extends Component {
  render() {
    return (
      <div className="App">
        <header className="App-header">
          <StreamInput />
          <p>Coming soon</p>
        </header>
      </div>
    );
  }
}

export default App;
