const hexToRgbChannels = (hexColor) => {
  const hexCode = parseInt(hexColor.slice(1), 16);
  var channels = [0, 0, 0];

  channels.forEach((_, i, channels) => {
    channels[2 - i] = (hexCode >> 8 * i) & 255;
  })

  return channels;
}

const hexToRgba = (hexColor, alpha) => {
  const channels = hexToRgbChannels(hexColor);

  return `rgba(${channels[0]}, ${channels[1]}, ${channels[2]}, ${alpha})`;
}

export { hexToRgbChannels, hexToRgba };
