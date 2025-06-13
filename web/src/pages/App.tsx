import { TOCTable } from '@/components/toc/TOCTable'
import { CombinedShowMovieForm } from '@/components/forms/ContentForm'
import { StatusScroller } from '@/components/status/StatusScroller'
import { AppContainer } from './App.styles'
import { ButtonBar } from '@/components/ButtonBar'
import { useContext, useState } from 'react'
import endpoints from '@/api/endpoints'
import { useAppDispatch, useAppSelector } from '@/api/store'
import { Context } from '@/components/socket/Context'
import { tocActions } from '@/api/store/toc'

function App() {
  const dispatch = useAppDispatch()
  const { setRipState, resetRipStatus } = useContext(Context)

  const [error, setError] = useState<boolean>()

  const sortInfo = useAppSelector((state) => state.rip.sort_info)
  const library = useAppSelector((state) => state.rip.destination?.library)
  const media = useAppSelector((state) => state.rip.destination?.media)
  const content = useAppSelector((state) => state.rip.destination?.content)
  const ripAll = useAppSelector((state) => state.rip.rip_all)

  const handleLoadTocClick = () => {
    console.info('Fetching TOC')
    setRipState && setRipState({})
    fetch(endpoints.toc(), { method: 'GET' })
      .then(response => response.json())
      .then(json => {
        dispatch(tocActions.setTocData(json))
      })
  }

  const handleStartRip = () => {
    fetch(endpoints.rip(), { 
      method: 'POST',
      body: JSON.stringify({
        rip_all: ripAll,
        destination: `${library}/${content}s/${media}`,
        sort_info: sortInfo
      }),
      headers: new Headers({
        "Content-Type": "application/json"
      })
    }).then((response) => {
      resetRipStatus && resetRipStatus();
      console.debug('handleStartRip() response', response)
    })
  }

  return (
    <AppContainer>
      {/* TODO: Add drive control buttons */}
      <ButtonBar 
        onLoadToc={handleLoadTocClick}
        onStartRip={handleStartRip}
        ripDisabled={error ?? true}
      />
      <CombinedShowMovieForm 
        onError={() => setError(true)}
        onClearError={() => setError(false)}
      />
      <TOCTable />
      <StatusScroller /> 
    </AppContainer>
  )
}

export default App
