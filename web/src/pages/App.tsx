import { AppContainer } from './App.styles'
import { ButtonBar } from '@/components/ButtonBar'
import { useAppDispatch } from '@/api'
import { StatusScroller } from '@/components/status/StatusScroller'
import { TocGrid } from '@/components/toc/TocGrid'
import { useGetErrorQuery } from '@/api/v1/error/api'
import { ErrorDialog } from '@/components/modals/ErrorDialog'
import { socketConnect } from '@/api/v1/socket/middleware'
import { CombinedShowMovieForm } from '@/components/forms/ContentForm'

function App() {
  const dispatch = useAppDispatch()

  const errorData = useGetErrorQuery()

  dispatch(socketConnect())

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
