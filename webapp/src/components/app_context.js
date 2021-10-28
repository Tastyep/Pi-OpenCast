import React from "react";
import { useLocalObservable } from "mobx-react-lite";
import { AppStore } from "./app_store";
import { SocketEventDispatcher } from "services/dispatcher";
import { listen as listenAppEvents } from "services/api/api";
import ModelFactory from "models/factory";

const AppContext = React.createContext(null);
const eventDispatcher = new SocketEventDispatcher([listenAppEvents()]);
const modelFactory = new ModelFactory(eventDispatcher);

export const AppProvider = ({ children }) => {
  const store = useLocalObservable(
    () => new AppStore(eventDispatcher, modelFactory)
  );

  return <AppContext.Provider value={store}>{children}</AppContext.Provider>;
};

export const useAppStore = () => React.useContext(AppContext);
