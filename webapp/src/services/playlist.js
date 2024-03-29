function queueNext(playlist, activeMediaId, mediaIds) {
  let mediaIdsCpy = Array.from(mediaIds);
  let activeMediaIdx = playlist.ids.indexOf(activeMediaId);

  // Remove the currently playing video from the given ids (if present)
  if (activeMediaIdx !== -1 && mediaIds !== playlist.ids) {
    const activeDuplicateIdx = mediaIds.indexOf(activeMediaId);

    if (activeDuplicateIdx !== -1) {
      mediaIdsCpy.splice(activeDuplicateIdx, 1);
    }
  }

  // Remove duplicates by removing already queued medias
  // [1,2,3] + [a,B,c,3] = [1,2,3,a,B,c]
  let ids = mediaIdsCpy.concat(playlist.ids);
  ids = [...new Set(ids)];
  if (activeMediaIdx === -1) {
    return ids;
  }

  // [1,2,3,a,B,c] -> [a,B] -> [a,B,1,2,3] -> [a,B,1,2,3,c]
  activeMediaIdx = ids.indexOf(activeMediaId, mediaIds.length);
  return ids
    .slice(mediaIdsCpy.length, activeMediaIdx + 1)
    .concat(ids.slice(0, mediaIdsCpy.length))
    .concat(ids.slice(activeMediaIdx + 1));
}

function queueLast(playlist, activeMediaId, mediaIds) {
  let mediaIdsCpy = Array.from(mediaIds);
  let activeMediaIdx = playlist.ids.indexOf(activeMediaId);

  // Remove the currently playing video from the given ids (if present)
  if (activeMediaIdx !== -1) {
    const activeDuplicateIdx = mediaIds.indexOf(activeMediaId);

    if (activeDuplicateIdx !== -1) {
      mediaIdsCpy.splice(activeDuplicateIdx, 1);
    }
  }

  // Remove duplicates by removing already queued medias
  // [1,2,3] + [a,B,c,3] = [1,2,3,a,B,c]
  let ids = mediaIdsCpy.concat(playlist.ids);
  ids = [...new Set(ids)];

  // [1,2,3,a,B,c] -> [a,B,c,1,2,3]
  return ids.slice(mediaIdsCpy.length).concat(ids.slice(0, mediaIdsCpy.length));
}

function shuffleIds(ids) {
  let shuffledIds = Array.from(ids);

  for (let i = shuffledIds.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [shuffledIds[i], shuffledIds[j]] = [shuffledIds[j], shuffledIds[i]];
  }

  return shuffledIds;
}

function filterVideos(artists, albums, videos, input) {
  if (input === "") {
    return videos;
  }

  const lowerInput = input.toLowerCase();
  return videos.filter((video) => {
    const artist = artists[video.artist_id];
    const album = albums[video.album_id];
    return (
      video.title.toLowerCase().includes(lowerInput) ||
      (artist && artist.name.toLowerCase().includes(lowerInput)) ||
      (album && album.name.toLowerCase().includes(lowerInput))
    );
  });
}

export { queueNext, queueLast, shuffleIds, filterVideos };
