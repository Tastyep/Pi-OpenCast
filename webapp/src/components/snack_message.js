import React, { useState, forwardRef, useCallback } from "react";
import { useSnackbar, SnackbarContent } from "notistack";

import { makeStyles } from "@mui/styles";
import Box from "@mui/material/Box";
import Collapse from "@mui/material/Collapse";
import Paper from "@mui/material/Paper";
import Typography from "@mui/material/Typography";
import Card from "@mui/material/Card";
import CardActions from "@mui/material/CardActions";
import IconButton from "@mui/material/IconButton";
import Stack from "@mui/material/Stack";
import List from "@mui/material/List";
import ListItem from "@mui/material/ListItem";

import CloseIcon from "@mui/icons-material/Close";
import ExpandMoreIcon from "@mui/icons-material/ExpandMore";
import CheckCircleIcon from "@mui/icons-material/CheckCircle";
import ErrorIcon from "@mui/icons-material/Error";
import WarningIcon from "@mui/icons-material/Warning";
import InfoIcon from "@mui/icons-material/Info";

import clsx from "clsx";

const useStyles = makeStyles({
  default: {
    background: "#313131",
  },
  error: {
    background: "#D32F2F",
  },
  warning: {
    background: "#FF9800",
  },
  info: {
    background: "#2196F3",
  },
  success: {
    background: "#43A047",
  },
  actionRoot: {
    padding: "8px 8px 8px 16px",
    justifyContent: "space-between",
  },
  expand: {
    transform: "rotate(0deg)",
  },
  button: {
    padding: "8px 8px",
    color: "rgba(0,0,0,0.6)",
  },
  expandOpen: {
    transform: "rotate(180deg)",
  },
});

const icons = {
  error: <ErrorIcon />,
  warning: <WarningIcon />,
  info: <InfoIcon />,
  success: <CheckCircleIcon />,
};

const SnackMessage = forwardRef((props, ref) => {
  const { closeSnackbar } = useSnackbar();
  const [expanded, setExpanded] = useState(false);
  const classes = useStyles();

  const { id, message, options, details } = props;
  const icon = icons[options.variant];

  const handleExpandClick = useCallback(() => {
    setExpanded((oldExpanded) => !oldExpanded);
  }, []);

  const handleDismiss = useCallback(() => {
    closeSnackbar(id);
  }, [id, closeSnackbar]);

  return (
    <SnackbarContent ref={ref}>
      <Card
        className={classes[options.variant]}
        sx={{ width: "100%", maxWidth: "500px" }}
      >
        <CardActions className={classes.actionRoot}>
          <Stack direction="row" sx={{ color: "#FFFFFF" }}>
            <Box sx={{ marginRight: "8px" }}>{icon && icon}</Box>
            <Typography
              variant="subtitle2"
              sx={{ alignSelf: "center", fontWeight: "bold" }}
            >
              {message}
            </Typography>
          </Stack>
          <div>
            {details && (
              <IconButton
                aria-label="Show more"
                className={`${clsx(classes.expand, {
                  [classes.expandOpen]: expanded,
                })} ${classes.button}`}
                onClick={handleExpandClick}
              >
                <ExpandMoreIcon />
              </IconButton>
            )}
            <IconButton
              className={` ${classes.expand} ${classes.button}`}
              onClick={handleDismiss}
            >
              <CloseIcon />
            </IconButton>
          </div>
        </CardActions>
        {details && (
          <Collapse in={expanded} timeout="auto" unmountOnExit>
            <Paper sx={{ borderRadius: "0px" }}>
              <List>
                {Object.entries(details).map(([key, value]) => (
                  <ListItem key={key}>
                    <Stack
                      direction="row"
                      alignItems="center"
                      sx={{ width: "100%" }}
                    >
                      <Typography
                        sx={{
                          flex: "2 1 0",
                          marginRight: "8px",
                          fontWeight: "bold",
                        }}
                      >
                        {key}:
                      </Typography>
                      <Typography sx={{ flex: "8 1 0", wordWrap: "anywhere" }}>
                        {value}
                      </Typography>
                    </Stack>
                  </ListItem>
                ))}
              </List>
            </Paper>
          </Collapse>
        )}
      </Card>
    </SnackbarContent>
  );
});

export default SnackMessage;
