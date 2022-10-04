const pluralize = require("pluralize");

function durationToHMS(msDuration, maxParts = null) {
  const date = new Date(msDuration);
  const parts = [date.getSeconds(), date.getUTCMinutes(), date.getUTCHours()];
  let hms_duration = "";

  if (maxParts === null) {
    maxParts = countHMSParts(msDuration);
  }
  const partCount = maxParts === 0 ? parts.length : Math.min(parts.length, maxParts);
  for (let i = 0; i < partCount; i++) {
    const part = parts[i];

    if (hms_duration === "") {
      hms_duration = part.toString().padStart(2, "0");
    } else {
      hms_duration = part.toString().padStart(2, "0") + ":" + hms_duration;
    }
  };

  return hms_duration;
}

function countHMSParts(msDuration) {
  const date = new Date(msDuration);
  const parts = [date.getSeconds(), date.getUTCMinutes(), date.getUTCHours()];

  let count = 0;
  parts.forEach(part => {
    if (part !== 0) {
      count++;
    } else {
      return count;
    }
  });

  return count;
}

function humanReadableDuration(duration) {
  const date = new Date(duration * 1000);
  const parts = [
    { hour: date.getUTCHours() },
    { minute: date.getUTCMinutes() },
    { second: date.getSeconds() },
  ];
  let format_duration = "";

  parts.forEach((part) => {
    const value = Object.values(part)[0];
    if (value === 0) {
      return;
    }
    if (format_duration !== "") {
      format_duration = format_duration + ", ";
    }
    format_duration =
      format_duration + pluralize(Object.keys(part)[0], value, true);
  });

  return format_duration;
}

export { durationToHMS, humanReadableDuration, countHMSParts };
