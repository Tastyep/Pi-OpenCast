import { useState, useEffect } from "react";

import { observer } from "mobx-react-lite";
import { autorun } from "mobx";

import { withSnackbar } from "notistack";

import { useAppStore } from "providers/app_context";

const Notifier = observer((props) => {
  const store = useAppStore();

  const [displayed, setDisplayed] = useState([]);

  useEffect(() => {
    const storeDisplayed = (id) => {
      setDisplayed([...displayed, id]);
    };

    autorun(() => {
      const notifications = store.notifications;

      notifications.forEach((notification) => {
        // Do nothing if snackbar is already displayed
        if (displayed.includes(notification.key)) return;
        // Display snackbar using notistack
        props.enqueueSnackbar(notification.message, notification.options);
        // Keep track of snackbars that we've displayed
        storeDisplayed(notification.key);
        // Dispatch action to remove snackbar from mobx store
        store.removeSnackbar(notification.key);
      });
    });
  }, [store, props, displayed]);

  return null;
});

export default withSnackbar(Notifier);
