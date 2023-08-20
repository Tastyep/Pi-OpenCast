import React, { useState } from "react";

import ButtonGroup from "@mui/material/ButtonGroup";
import Button from "@mui/material/Button";

import { observer } from "mobx-react-lite";

function findCategories(collection, categoryFactory) {
  let categories = new Set();

  for (const item of collection) {
    const category = categoryFactory(item)[0];

    if (!categories.has(category)) {
      categories.add(category);
    }
  }

  return Array.from(categories).sort();
}

const FilterButtonGroup = observer((props) => {
  const {
    collection,
    clickHandle,
    categoryFactory,
    selectedButtonValue,
    sx,
    children,
  } = props;
  const [selectedButton, setSelectedButton] = useState(selectedButtonValue);
  const nameCategories = findCategories(collection, categoryFactory);

  const childrenWithProps = React.Children.map(children, (child) => {
    const handleClick = (event) => {
      if (child.props.onClick) {
        child.props.onClick(event);
      }

      setSelectedButton(child.props.value);
      clickHandle(child.props.value);
    };
    const variant =
      selectedButton === child.props.value ? "contained" : "outlined";

    return React.cloneElement(child, {
      onClick: handleClick,
      variant: variant,
    });
  });

  return (
    <ButtonGroup variant="contained" color="primary" sx={sx}>
      {childrenWithProps}
      {nameCategories.map((nameCategory, _) => (
        <Button
          key={nameCategory}
          onClick={() => {
            setSelectedButton(nameCategory);
            clickHandle(nameCategory);
          }}
          variant={selectedButton === nameCategory ? "contained" : "outlined"}
        >
          {nameCategory}
        </Button>
      ))}
    </ButtonGroup>
  );
});

export default FilterButtonGroup;
