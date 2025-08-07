import { CombinedShowMovieForm } from '@/components/forms/ContentForm'
import { AppContainer } from './App.styles'
import { ButtonBar } from '@/components/ButtonBar'
import { useEffect } from 'react'
import { endpoints, type ApiModel } from '@/api/endpoints'
import { useAppDispatch, useAppSelector } from '@/api/store'
import { tocActions } from '@/api/store/toc'
import { tmdbActions } from '@/api/store/tmdb'
import type { ApiState } from '@/api/v1/types/State'
import { ripActions } from '@/api/store/rip'
import { StatusScroller } from '@/components/status/StatusScroller'
import { TOCGrid } from '@/components/toc/TOCGrid'
import type { APIResponse } from '@/api/v1'

function App() {
  const dispatch = useAppDispatch()

  const tmdbConfiguration = useAppSelector((state) => state.tmdb.configuration)

  if (!tmdbConfiguration) {
    fetch(endpoints.tmdb.configuration())
      .then(response => response.json() as Promise<ApiModel['v1']['tmdb/configuration']>)
      .then(({ data }) => {
        dispatch(tmdbActions.setTmdbConfiguration(data))
      })
  }

  useEffect(() => {
    fetch(endpoints.state.get("redux/rip"), { method: 'GET' })
      .then(response => response.json() as Promise<ApiModel['v1']['state']>) 
      .then(({ data } ) => {
        if (data.redux?.rip) {
        dispatch(ripActions.setRipData(data.redux.rip))
        }
      })

    fetch(endpoints.state.get("redux/toc"), { method: 'GET' })
      .then(response => response.json() as Promise<ApiModel['v1']['state']>)
      .then(({ data }) => {
        if (data.redux?.toc) {
          dispatch(tocActions.setTocData(data.redux.toc))
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
