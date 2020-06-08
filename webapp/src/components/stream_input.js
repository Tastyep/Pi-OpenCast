import React, { Component } from "react";
import player from "services/api/player";

class StreamInput extends Component {
  constructor(props) {
    super(props);
    this.state = { value: "", action: undefined };

    this.onChange = this.onChange.bind(this);
    this.onSubmit = this.onSubmit.bind(this);
    this.streamMedia = this.streamMedia.bind(this);
    this.queueMedia = this.queueMedia.bind(this);
  }

  onChange(event) {
    this.setState({ value: event.target.value });
  }

  streamMedia(event) {
    this.setState({ action: player.streamMedia });
  }

  queueMedia(event) {
    this.setState({ action: player.queueMedia });
  }

  onSubmit(event) {
    console.log("PASS ", this.state);
    event.preventDefault();
    let url = this.state.value;
    if (url === "") {
      return;
    }
    this.state.action(url);
    this.setState({ value: "", action: undefined });
  }

  render() {
    return (
      <form onSubmit={this.onSubmit}>
        <input
          type="search"
          placeholder="Media's URL"
          value={this.state.value}
          onChange={this.onChange}
        />
        <br />
        <input
          type="submit"
          name="cast"
          value="Cast"
          onClick={this.streamMedia}
        />
        <input
          type="submit"
          name="queue"
          value="Queue"
          onClick={this.queueMedia}
        />
      </form>
    );
  }
}

export default StreamInput;
