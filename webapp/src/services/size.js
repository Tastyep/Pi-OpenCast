import { useState, useEffect } from "react";
import useMediaQuery from "@mui/material/useMediaQuery";

import { SIZES } from "constants.js";

const generateMediaQuery = (size) => {
  const { min, max } = SIZES[size];
  let query = "";

  if (min) {
    query += `(min-width: ${min}px)`;
  }

  if (min && max) {
    query += " and ";
  }

  if (max) {
    query += `(max-width: ${max}px)`;
  }

  return query;
};

function useActiveSize() {
  // There has to be a better way
  const isSmall = useMediaQuery(generateMediaQuery("small"));
  const isMedium = useMediaQuery(generateMediaQuery("medium"));
  const isLarge = useMediaQuery(generateMediaQuery("large"));
  const isXLarge = useMediaQuery(generateMediaQuery("xlarge"));
  const isXXLarge = useMediaQuery(generateMediaQuery("xxlarge"));

  if (isSmall) return "small";
  if (isMedium) return "medium";
  if (isLarge) return "large";
  if (isXLarge) return "xlarge";
  if (isXXLarge) return "xxlarge";

  return null;
}

export { useActiveSize };
