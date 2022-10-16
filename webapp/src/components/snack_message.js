import React, { useState, forwardRef, useCallback } from "react";
import { useSnackbar, SnackbarContent } from "notistack";

import { styled } from "@mui/styles";
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

import { useTheme } from "@emotion/react";

const NotifCard = (props) => {
  const { colorScheme, children } = props;
  const theme = useTheme();

  return (<Card sx={{
    background: colorScheme.main
  }} >{children} </Card>);
};

const NotifIcon = (props) => {
  const { variant, colorScheme, sx } = props;
  const theme = useTheme();

  const icons = {
    error: <ErrorIcon sx={{ color: colorScheme.dark }} />,
    warning: <WarningIcon sx={{ color: colorScheme.dark }} />,
    info: <InfoIcon sx={{ color: colorScheme.dark }} />,
    success: <CheckCircleIcon sx={{ color: colorScheme.dark }} />,
  };
  const icon = icons[variant];

  return <Box sx={sx}>{icon}</Box>
};

const NotifCardActions = styled(CardActions)({
  padding: "8px 8px 8px 16px",
  justifyContent: "space-between",
});


const SnackMessage = forwardRef((props, ref) => {
  const { id, message, options, details } = props;

  const { closeSnackbar } = useSnackbar();
  const [expanded, setExpanded] = useState(false);

  const theme = useTheme();
  const colorScheme = theme.palette[options.variant];

  const handleExpandClick = useCallback(() => {
    setExpanded((oldExpanded) => !oldExpanded);
  }, []);

  const handleDismiss = useCallback(() => {
    closeSnackbar(id);
  }, [id, closeSnackbar]);

  return (
    <SnackbarContent ref={ref}>
      <NotifCard
        colorScheme={colorScheme}
        sx={{ width: "100%", maxWidth: "500px" }}
      >
        <NotifCardActions>
          <Stack direction="row">
            <NotifIcon variant={options.variant} colorScheme={colorScheme} sx={{ marginRight: "8px" }} />
            <Typography
              variant="subtitle2"
              sx={{ alignSelf: "center", fontWeight: "bold", color: colorScheme.contrastText }}
            >
              {message}
            </Typography>
          </Stack>
          <div>
            {details && (
              <IconButton
                aria-label="Show more"
                sx={{ transform: expanded ? "rotate(180deg)" : "rotate(0deg)", color: colorScheme.dark }}
                onClick={handleExpandClick}
              >
                <ExpandMoreIcon />
              </IconButton>
            )}
            <IconButton
              sx={{ color: colorScheme.dark }}
              onClick={handleDismiss}
            >
              <CloseIcon />
            </IconButton>
          </div>
        </NotifCardActions>
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
      </NotifCard>
    </SnackbarContent >
  );
});

export default SnackMessage;
