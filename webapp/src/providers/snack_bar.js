import { SnackbarProvider as NotistackProvider } from "notistack";

import MediaQuery from "react-responsive";
import { SIZES } from "constants.js";

const SnackBarProvider = (props) => {
  const { children } = props;

  return (
    <MediaQuery maxWidth={SIZES.small.max}>
      {(matches) =>
        matches ? (
          <NotistackProvider
            dense
            maxSnack={2}
            anchorOrigin={{
              vertical: "bottom",
              horizontal: "center",
            }}
          >
            {children}
          </NotistackProvider>
        ) : (
          <NotistackProvider
            maxSnack={5}
            anchorOrigin={{
              vertical: "top",
              horizontal: "right",
            }}
          >
            {children}
          </NotistackProvider>
        )
      }
    </MediaQuery>
  );
};

export default SnackBarProvider;
