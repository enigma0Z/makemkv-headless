import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import { BrowserRouter, Route, Routes } from 'react-router'
import App from '@/pages/App'
import { Provider } from 'react-redux'
import { store } from './api'
import { ThemeProvider } from '@emotion/react'
import { theme } from './theme'
import { CssBaseline } from '@mui/material'
import { StatusScroller } from './components/status/StatusScroller'

// TODO: This should really be in react middleware, but it's not currently This
// class auto-connects to the socket on app load, but its all self-contained, so
// there's no actual components or items to import (there used to be).  Point
// is, don't comment it out until it's in middleware or else the socket
// connection will break :D 
import './components/socket' 

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Provider store={store} >
        <BrowserRouter>
          <Routes>
            <Route path="/" element={<App />} />
            <Route path="/status" element={<StatusScroller />} />
          </Routes>
        </BrowserRouter>
      </Provider>
    </ThemeProvider>
  </StrictMode>
)
