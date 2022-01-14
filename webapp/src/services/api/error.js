const snackBarHandler = (store) => {
  return (error) => {
    if (!error.response) {
      return;
    }

    store.enqueueSnackbar(
      {
        message: error.response.data.message,
        options: {
          variant: "error",
        },
      },
      error.response.data.details
    );
  };
};

export default snackBarHandler;
