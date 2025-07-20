import { CombinedShowMovieForm } from '@/components/forms/ContentForm'
import { AppContainer } from './App.styles'
import { ButtonBar } from '@/components/ButtonBar'
import { useEffect } from 'react'
import endpoints from '@/api/endpoints'
import { useAppDispatch, useAppSelector } from '@/api/store'
import { tocActions } from '@/api/store/toc'
import { tmdbActions } from '@/api/store/tmdb'
import type { ApiState } from '@/api/types/status'
import { ripActions } from '@/api/store/rip'
import { StatusScroller } from '@/components/status/StatusScroller'
import { TOCGrid } from '@/components/toc/TOCGrid'

function App() {
  const dispatch = useAppDispatch()

  const tmdbConfiguration = useAppSelector((state) => state.tmdb.configuration)

  if (!tmdbConfiguration) {
    fetch(endpoints.tmdb.configuration())
      .then(response => response.json())
      .then(json => {
        dispatch(tmdbActions.setTmdbConfiguration(json))
      })
  }

  useEffect(() => {
    fetch(endpoints.state.get("redux/rip"), { method: 'GET' })
      .then(response => response.json() as Promise<ApiState>) 
      .then((json) => {
        if (json.redux?.rip) {
        dispatch(ripActions.setRipData(json.redux.rip))
        }
      })

    fetch(endpoints.state.get("redux/toc"), { method: 'GET' })
      .then(response => response.json() as Promise<ApiState>)
      .then((json) => {
        if (json.redux?.toc) {
          dispatch(tocActions.setTocData(json.redux.toc))
        }
      })
  }, []);

  return (
    <AppContainer>
      <ButtonBar />
      <CombinedShowMovieForm />
      <TOCGrid />
      <StatusScroller /> 
    </AppContainer>
  )
}

export default App
