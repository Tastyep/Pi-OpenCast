const hexToRgbChannels = (hexColor) => {
  if (hexColor.startsWith("#")) {
    hexColor = hexColor.slice(1);
  }
  if (hexColor.length === 6) {
    // prepend alpha
    hexColor = "FF" + hexColor;
  }
  let hexCode = parseInt(hexColor, 16);
  var channels = [0, 0, 0, 0];

  channels.forEach((_, i, channels) => {
    channels[3 - i] = (hexCode >> (8 * i)) & 255;
  });

  return channels;
};

const hexToRgba = (hexColor, alpha) => {
  const channels = hexToRgbChannels(hexColor);

  return `rgba(${channels[1]}, ${channels[2]}, ${channels[3]}, ${alpha})`;
};

const mixColor = (hexColor, otherColor, ratio) => {
  const channels = hexToRgbChannels(hexColor);
  const otherChannels = hexToRgbChannels(otherColor);

  channels.forEach((channel, i, channels) => {
    channels[i] = (1 - ratio) * channel + ratio * otherChannels[i];
  });

  return `rgba(${channels[1]}, ${channels[2]}, ${channels[3]}, ${channels[0]})`;
};

export { hexToRgbChannels, hexToRgba, mixColor };
