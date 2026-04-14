import { CombinedShowMovieForm } from '@/components/forms/ContentForm'
import { AppContainer } from './App.styles'
import { ButtonBar } from '@/components/ButtonBar'
import { useEffect, useState } from 'react'
import { endpoints, type ApiModel } from '@/api/endpoints'
import { useAppDispatch, useAppSelector } from '@/api'
import { tocActions } from '@/api/v1/toc/store'
import { tmdbActions } from '@/api/v1/tmdb/store'
import { ripActions } from '@/api/v1/rip/store'
import { StatusScroller } from '@/components/status/StatusScroller'
import { TocGrid } from '@/components/toc/TocGrid'
import { useGetStateByPathQuery } from '@/api/v1/state/api'
import { useGetErrorQuery } from '@/api/v1/error/api'
import { ErrorDialog } from '@/components/modals/ErrorDialog/ErrorDialog'

function App() {
  const dispatch = useAppDispatch()

  const tmdbConfiguration = useAppSelector((state) => state.tmdb.configuration)
  const ripStateData = useGetStateByPathQuery('redux/rip').data?.redux.rip
  const errorData = useGetErrorQuery()

  dispatch(ripActions.setRipData(ripStateData))

  if (!tmdbConfiguration) {
    fetch(endpoints.tmdb.configuration())
      .then(response => response.json() as Promise<ApiModel['v1']['tmdb/configuration']>)
      .then(({ data }) => {
        dispatch(tmdbActions.setTmdbConfiguration(data))
      })
  }

  useEffect(() => {
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
      <TocGrid />
      <StatusScroller /> 
      <ErrorDialog 
        open={!errorData.isLoading && errorData.currentData !== null} 
        errorData={errorData.data} 
      />
    </AppContainer>
  )
}

export default App
