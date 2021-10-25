function queueNext(playlist, activeMediaId, mediaId) {
  let ids = Array.from(playlist.ids);
  const activeIdx = ids.indexOf(activeMediaId);
  const mediaIdx = ids.indexOf(mediaId);
  const insertIdx = activeIdx === -1 ? 0 : activeIdx + 1;

  if (mediaIdx === -1) {
    ids.splice(insertIdx, 0, mediaId);
  } else {
    // move the media to its new position
    ids.splice(insertIdx, 0, ids.splice(mediaIdx, 1)[0]);
  }
  return ids;
}

function queueLast(playlist, mediaId) {
  let ids = Array.from(playlist.ids);
  const mediaIdx = ids.indexOf(mediaId);

  if (mediaIdx !== -1) {
    ids.splice(mediaIdx, 1);
  }
  ids.push(mediaId);
  return ids;
}

export { queueNext, queueLast };
