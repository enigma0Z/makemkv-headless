import { TOCTable } from '@/components/toc/TOCTable'
import { CombinedShowMovieForm } from '@/components/forms/ContentForm'
import { StatusScroller } from '@/components/status/StatusScroller'
import { AppContainer } from './App.styles'
import { ButtonBar } from '@/components/ButtonBar'
import { useContext, useEffect, useState } from 'react'
import endpoints from '@/api/endpoints'
import { useAppDispatch, useAppSelector } from '@/api/store'
import { Context } from '@/components/socket/Context'
import { tocActions } from '@/api/store/toc'
import { tmdbActions } from '@/api/store/tmdb'
import type { ApiState } from '@/api/types/status'
import { ripActions } from '@/api/store/rip'
import { ConfirmationDialog } from '@/components/ConfirmationModal'

function App() {
  const dispatch = useAppDispatch()
  const { ripState, setRipState, resetRipState } = useContext(Context)

  const [error, setError] = useState<boolean>()
  const [cancelModalOpen, setCancelModalOpen] = useState<boolean>(false)

  const sortInfo = useAppSelector((state) => state.rip.sort_info)
  const library = useAppSelector((state) => state.rip.destination?.library)
  const media = useAppSelector((state) => state.rip.destination?.media)
  const content = useAppSelector((state) => state.rip.destination?.content)
  const ripAll = useAppSelector((state) => state.rip.rip_all)
  const tmdbConfiguration = useAppSelector((state) => state.tmdb.configuration)

  if (!tmdbConfiguration) {
    fetch(endpoints.tmdb.configuration())
      .then(response => response.json())
      .then(json => {
        dispatch(tmdbActions.setTmdbConfiguration(json))
      })
  }

  const handleEject= () => {
    console.info('Ejecting disc')
    resetRipState && resetRipState()
    fetch(endpoints.eject(), { method: 'GET' })
  }

  const handleLoadTocClick = () => {
    console.info('Fetching TOC')
    resetRipState && resetRipState()
    dispatch(tocActions.setTocData(undefined))
    // fetch(endpoints.state.resetSocket(), { method: 'GET' })
    fetch(endpoints.toc(), { method: 'GET' })
      .then(response => response.json())
      .then(json => {
        dispatch(tocActions.setTocData(json))
      })
  }

  const handleCancelRip = () => {
    fetch(endpoints.rip.stop(), { 
      method: 'GET'
    }).then((response) => {
      setRipState && setRipState({ rip_started: false })
      console.log('Rip stop response', response)
    })
  };

  const handleStartRip = () => {
    if (ripState?.rip_started) {
      setCancelModalOpen(true)
    } else {
      setRipState && setRipState({ rip_started: true })
      fetch(endpoints.rip.start(), { 
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
        resetRipState && resetRipState();
      })
    }
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
      {/* TODO: Add drive control buttons */}
      <ButtonBar 
        onEject={handleEject}
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
      <ConfirmationDialog
        open={cancelModalOpen}
        onClose={() => { setCancelModalOpen(false) } }
        onConfirm={() => { handleCancelRip() } } 
        title={'Cancel Rip?'} 
        message={'This disc will not get uploaded if it is cancelled now'}
      />
    </AppContainer>
  )
}

export default App
