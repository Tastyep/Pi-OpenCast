class SizeEntry {
  constructor(min, max) {
    this.min = min;
    this.max = max;
  }

  compareTo(other) {
    return this.min - other.min;
  }
}

const SIZES = {
  small: new SizeEntry(0, 599),
  medium: new SizeEntry(600, 999),
  large: new SizeEntry(1000, 1199),
  xlarge: new SizeEntry(1200, 1399),
  xxlarge: new SizeEntry(1400, undefined),
};

const MARGINS = {
  small: { margin: "8px" },
  medium: { margin: "8px" },
  large: { margin: "16px" },
  xlarge: { margin: "16px" },
  xxlarge: { margin: "24px" },
};

export { SIZES, MARGINS };
