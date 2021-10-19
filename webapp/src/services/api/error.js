const snackBarHandler = (store) => {
  return (error) =>
    store.enqueueSnackbar({
      message: error.response.data.message,
      options: {
        variant: "error",
      },
    });
};

export default snackBarHandler;
