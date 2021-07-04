export default class Video {
  constructor(state) {
    this.id = state.id;
    this.source = state.source;
    this.sourceProtocol = state.source_protocol;
    this.title = state.title;
    this.collectionId = state.collection_id;
    this.thumbnail = state.thumbnail;
    this.location = state.location;
    this.streams = state.streams;
    this.subtitle = state.subtitle;
  }
}
