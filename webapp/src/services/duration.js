function duration_to_hms(duration) {
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

export { duration_to_hms };
