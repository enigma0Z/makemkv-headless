import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import { BrowserRouter, Route, Routes } from 'react-router'
import App from '@/pages/App'
import { Provider } from 'react-redux'
import { store } from './api/store'
import { StatusScroller } from './components/status/StatusScroller'
import { ThemeProvider } from '@emotion/react'
import { theme } from './theme'
import { CssBaseline } from '@mui/material'
import SocketConnection from './components/socket/Connection'
import SocketContext from './components/socket/Context'

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Provider store={store} >
        <SocketContext>
          <SocketConnection />
          <BrowserRouter>
            <Routes>
              <Route path="/" element={<App />} />
              <Route path="/status" element={<StatusScroller />} />
            </Routes>
          </BrowserRouter>
        </SocketContext>
      </Provider>
    </ThemeProvider>
  </StrictMode>
)
