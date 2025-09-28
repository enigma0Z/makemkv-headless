import { Button, Dialog, DialogActions, DialogContent, DialogTitle, IconButton, TextField, Typography } from "@mui/material"
import { ConfigDialogActions, ConfigDialogContent, ConfigDialogTitle } from "./ConfigDialog.styles"

import RefreshIcon from '@mui/icons-material/Refresh';
import CloseIcon from '@mui/icons-material/Close';
import { useGetConfigQuery, useReloadConfigQuery } from "@/api/v1/config/api";
import { useEffect, useState } from "react";
import type { Config } from "@/api/v1/config/types";

type Props = {
  open: boolean
  onClose?: () => void
}

export const ConfigDialog = ({ open, onClose = () => {} }: Props) => {
  const { data, refetch: refetchConfig, isLoading, isSuccess } = useGetConfigQuery()
  const { refetch: reloadConfig } = useReloadConfigQuery()

  const [ tmdbToken, setTmdbToken ] = useState<Config['tmdb_token'] | null>(null)
  const [ makemkvconPath, setMakemkvconPath ] = useState<Config['makemkvcon_path'] | null>(null)
  const [ source, setSource ] = useState<Config['source'] | null>(null)
  const [ destination, setDestination ] = useState<Config['destination'] | null>(null)
  const [ tempPrefix, setTempPrefix ] = useState<Config['temp_prefix'] | null>(null)
  const [ logLevel, setLogLevel ] = useState<Config['log_level'] | null>(null)
  const [ frontend, setFrontend ] = useState<Config['frontend'] | null>(null)

  useEffect(() => {
    if (!isLoading && isSuccess) {
      setFormFromApi(data)
    }
  }, [isLoading, isSuccess])
  
  const setFormFromApi = (data: Config) => {
    setTmdbToken(data.tmdb_token)
    setMakemkvconPath(data.makemkvcon_path)
    setSource(data.source)
    setDestination(data.destination)
    setTempPrefix(data.temp_prefix)
    setLogLevel(data.log_level)
    setFrontend(data.frontend)
  }

  const handleClose = () => { onClose() }  
  
  const handleSave = () => { 
    onClose() 
  }

  const handleRefresh = () => {
    console.debug('handleRefresh()')
    reloadConfig().then(({ data }) => {
      data && setFormFromApi(data)
    })
  }

  return <Dialog open={open} onClose={handleClose}>
    <ConfigDialogTitle>
      <IconButton onClick={handleRefresh}><RefreshIcon /></IconButton>
      <Typography variant="h4">Settings</Typography>
      <IconButton onClick={handleClose}><CloseIcon /></IconButton>
    </ConfigDialogTitle>
    <ConfigDialogContent>
      <TextField fullWidth margin="normal" label="TMDB API Token" value={tmdbToken} />
      <TextField fullWidth margin="normal" label="Makemkvcon Path" value={makemkvconPath} />
      <TextField fullWidth margin="normal" label="Source" value={source} />
      <TextField fullWidth margin="normal" label="Destination" value={destination} />
      <TextField fullWidth margin="normal" label="Temp Prefix" value={tempPrefix} />
      <TextField fullWidth margin="normal" label="Log Level" value={logLevel}/>
      <TextField fullWidth margin="normal" label="Frontend Address" value={frontend} />
    </ConfigDialogContent>
    <ConfigDialogActions>
      <Button onClick={handleClose}>Cancel</Button>
      <Button onClick={handleSave} variant="contained">Save</Button>
    </ConfigDialogActions>
  </Dialog>
}