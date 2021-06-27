import React from 'react'
import { useLocalObservable } from 'mobx-react-lite'
import { AppStore } from './app_store'

const AppContext = React.createContext(null)

export const AppProvider = ({children}) => {
  const store = useLocalObservable(() => new AppStore())

  return <AppContext.Provider value={store}>
      {children}
    </AppContext.Provider>
}

export const useAppStore = () => React.useContext(AppContext)
