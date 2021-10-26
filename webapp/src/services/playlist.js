function queueNext(playlist, activeMediaId, mediaIds) {
  let activeMediaIdx = playlist.ids.indexOf(activeMediaId);

  // Remove the currently playing video from the given ids (if present)
  if (activeMediaIdx !== -1) {
    const activeDuplicateIdx = mediaIds.indexOf(activeMediaId);

    if (activeDuplicateIdx !== -1) {
      mediaIds.splice(activeDuplicateIdx, 1);
    }
  }

  // Remove duplicates by removing already queued medias
  // [1,2,3] + [a,B,c,3] = [1,2,3,a,B,c]
  let ids = mediaIds.concat(Array.from(playlist.ids));
  ids = [...new Set(ids)];
  if (activeMediaIdx === -1) {
    return ids;
  }

  // [1,2,3,a,B,c] -> [a,B] -> [a,B,1,2,3] -> [a,B,1,2,3,c]
  activeMediaIdx = ids.indexOf(activeMediaId, mediaIds.length);
  return ids
    .slice(mediaIds.length, activeMediaIdx + 1)
    .concat(ids.slice(0, mediaIds.length))
    .concat(ids.slice(activeMediaIdx + 1));
}

function queueLast(playlist, activeMediaId, mediaIds) {
  let activeMediaIdx = playlist.ids.indexOf(activeMediaId);

  // Remove the currently playing video from the given ids (if present)
  if (activeMediaIdx !== -1) {
    const activeDuplicateIdx = mediaIds.indexOf(activeMediaId);

    if (activeDuplicateIdx !== -1) {
      mediaIds.splice(activeDuplicateIdx, 1);
    }
  }

  // Remove duplicates by removing already queued medias
  // [1,2,3] + [a,B,c,3] = [1,2,3,a,B,c]
  let ids = mediaIds.concat(Array.from(playlist.ids));
  ids = [...new Set(ids)];

  // [1,2,3,a,B,c] -> [a,B,c,1,2,3]
  return ids.slice(mediaIds.length).concat(ids.slice(0, mediaIds.length));
}

export { queueNext, queueLast };
