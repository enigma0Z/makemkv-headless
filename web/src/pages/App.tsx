import { AppContainer } from './App.styles'
import { ButtonBar } from '@/components/ButtonBar'
import { endpoints, type ApiModel } from '@/api/endpoints'
import { useAppDispatch, useAppSelector } from '@/api'
import { tmdbActions } from '@/api/v1/tmdb/store'
import { StatusScroller } from '@/components/status/StatusScroller'
import { TocGrid } from '@/components/toc/TocGrid'
import { useGetErrorQuery } from '@/api/v1/error/api'
import { ErrorDialog } from '@/components/modals/ErrorDialog'
import { socketConnect } from '@/api/v1/socket/middleware'
import { CombinedShowMovieForm } from '@/components/forms/ContentForm'

function App() {
  const dispatch = useAppDispatch()

  const tmdbConfiguration = useAppSelector((state) => state.tmdb.configuration)
  const errorData = useGetErrorQuery()

  dispatch(socketConnect())

  if (!tmdbConfiguration) {
    fetch(endpoints.tmdb.configuration())
      .then(response => response.json() as Promise<ApiModel['v1']['tmdb/configuration']>)
      .then(({ data }) => {
        dispatch(tmdbActions.setTmdbConfiguration(data))
      })
  }

  return (
    <AppContainer>
      <ButtonBar />
      <CombinedShowMovieForm />
      <TocGrid />
      <StatusScroller /> 
      <ErrorDialog 
        open={!errorData.isLoading && errorData.currentData !== null} 
        errorData={errorData.currentData} 
      />
    </AppContainer>
  )
}

export default App
