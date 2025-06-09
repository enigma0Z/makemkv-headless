import { TOCTable } from '@/components/toc/TOCTable'
import { CombinedShowMovieForm } from '@/components/forms/ContentForm'
import { StatusScroller } from '@/components/status/StatusScroller'
import { AppContainer } from './App.styles'
import { ButtonBar } from '@/components/ButtonBar'
import { useState } from 'react'
import endpoints from '@/api/endpoints'
import type { Toc } from '@/api/types/Toc'
import { useAppSelector } from '@/api/store'

function App() {
  const [tocLoading, setTocLoading] = useState<boolean>()
  const [ripping, setRipping] = useState<boolean>()
  const [tocData, setTocData] = useState<Toc>()

  const sortInfo = useAppSelector((state) => state.rip.sort_info)
  const library = useAppSelector((state) => state.rip.destination?.library)
  const media = useAppSelector((state) => state.rip.destination?.media)
  const content = useAppSelector((state) => state.rip.destination?.content)
  const ripAll = useAppSelector((state) => state.rip.rip_all)

  const handleLoadTocClick = () => {
    console.info('Fetching TOC')
    setTocLoading(true)
    fetch(endpoints.toc(), { method: 'GET' })
      .then(response => response.json())
      .then(json => {
        console.log('response json', json)
        setTocData(json)
        setTocLoading(false)
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
      console.debug('handleStartRip() response', response)
    })
  }

  return (
    <AppContainer>
      {/* TODO: Add drive control buttons */}
      <ButtonBar 
        onLoadToc={handleLoadTocClick}
        onStartRip={handleStartRip}
      />
      <CombinedShowMovieForm />
      <TOCTable data={tocData} loading={tocLoading} />
      {/* TODO: Add rip controls and rip status view */}
      {/* TODO: Figure out how to make this a fixed height */}
      <StatusScroller /> 
    </AppContainer>
  )
}

export default App
