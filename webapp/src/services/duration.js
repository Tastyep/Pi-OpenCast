const pluralize = require("pluralize");

function durationToHMS(duration) {
  const date = new Date(duration * 1000);
  const parts = [date.getUTCHours(), date.getUTCMinutes(), date.getSeconds()];
  let hms_duration = "";

  parts.forEach((part) => {
    if (hms_duration === "") {
      if (part === 0) {
        return;
      }
      hms_duration = part.toString();
    } else {
      hms_duration = hms_duration + ":" + part.toString().padStart(2, "0");
    }
  });

  return hms_duration;
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
      format_duration = format_duration + " ";
    }
    format_duration =
      format_duration + pluralize(Object.keys(part)[0], value, true);
  });

  return format_duration;
}

export { durationToHMS, humanReadableDuration };
