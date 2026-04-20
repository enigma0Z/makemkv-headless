import { Button, Dialog, IconButton, TextField, Typography } from "@mui/material"

import RefreshIcon from '@mui/icons-material/Refresh';
import CloseIcon from '@mui/icons-material/Close';
import { useGetConfigQuery, usePutConfigMutation, useReloadConfigMutation } from "@/api/v1/config/api";
import { useState } from "react";
import type { Config } from "@/api/v1/config/types";
import { ConfigDialogActions, ConfigDialogContent, ConfigDialogTitle } from "./index.styles";

type Props = {
  open: boolean
  onClose?: () => void
}

export const ConfigDialog = ({ open, onClose = () => {} }: Props) => {
  const { data, isLoading, isSuccess } = useGetConfigQuery()
  const [putConfig, _putConfigResult] = usePutConfigMutation()
  const [reloadConfig, _reloadConfigResult] = useReloadConfigMutation()

  const [formData, setFormData] = useState<Partial<Config>>(!isLoading && isSuccess ? data : {})

  const config_file = formData?.config_file ?? data?.config_file ?? '';
  const source = formData?.source ?? data?.source ?? '';
  const destination = formData?.destination ?? data?.destination ?? '';
  const tmdb_token = formData?.tmdb_token ?? data?.tmdb_token ?? '';
  const makemkvcon_path = formData?.makemkvcon_path ?? data?.makemkvcon_path ?? '';
  // const log_level = formData?.log_level ?? data?.log_level ?? '';
  const log_file = formData?.log_file ?? data?.log_file ?? '';
  const temp_prefix = formData?.temp_prefix ?? data?.temp_prefix ?? '';
  const frontend = formData?.frontend ?? data?.frontend ?? '';
  const listen_port = formData?.listen_port ?? data?.listen_port ?? '';

  // useEffect(() => {
  //   if (!isLoading && isSuccess) {
  //     setFormFromApi(data)
  //   }
  // }, [isLoading, isSuccess])
  
  const handleClose = () => { onClose() }  
  
  const handleSave = () => { 
    putConfig(formData)
    onClose() 
  }

  const handleRefresh = () => {
    reloadConfig()
    setFormData({})
  }

  return <Dialog open={open} onClose={handleClose}>
    <ConfigDialogTitle>
      <IconButton onClick={handleRefresh}><RefreshIcon /></IconButton>
      <Typography variant="h4">Settings</Typography>
      <IconButton onClick={handleClose}><CloseIcon /></IconButton>
    </ConfigDialogTitle>
    <ConfigDialogContent>
      
      <TextField fullWidth margin="normal" label="Config File" 
        value={config_file} 
        onChange={(event) => setFormData((prev) => ({...prev, config_file: event.target.value})) }
      />
      <TextField fullWidth margin="normal" label="Source" 
        value={source} 
        onChange={(event) => setFormData((prev) => ({...prev, source: event.target.value})) }
      />
      <TextField fullWidth margin="normal" label="Destination" 
        value={destination} 
        onChange={(event) => setFormData((prev) => ({...prev, destination: event.target.value})) }
      />
      <TextField fullWidth margin="normal" label="TMDB API Token" 
        value={tmdb_token} 
        onChange={(event) => setFormData((prev) => ({...prev, tmdb_token: event.target.value})) }
      />
      <TextField fullWidth margin="normal" label="Makemkvcon Path" 
        value={makemkvcon_path} 
        onChange={(event) => setFormData((prev) => ({...prev, makemkvcon_path: event.target.value})) }
      />
      {/* 
      TODO: Make this one a select with log levels
      <TextField fullWidth margin="normal" label="Log Level" 
        value={log_level}
        onChange={(event) => setFormData((prev) => ({...prev, log_level: event.target.value})) }
      /> 
      */}
      <TextField fullWidth margin="normal" label="Log File" 
        value={log_file}
        onChange={(event) => setFormData((prev) => ({...prev, log_file: event.target.value})) }
      />
      <TextField fullWidth margin="normal" label="Temp Prefix" 
        value={temp_prefix} 
        onChange={(event) => setFormData((prev) => ({...prev, temp_prefix: event.target.value})) }
      />
      <TextField fullWidth margin="normal" label="Frontend Address" 
        value={frontend} 
        onChange={(event) => setFormData((prev) => ({...prev, frontend: event.target.value})) }
      />
      <TextField fullWidth margin="normal" label="Listen Port" 
        value={listen_port} 
        onChange={(event) => setFormData((prev) => ({...prev, listen_port: event.target.value})) }
      />
      {/* <TextField fullWidth margin="normal" label="UI Path" value={data?.ui_path} /> */}
    </ConfigDialogContent>
    <ConfigDialogActions>
      <Button onClick={handleClose}>Cancel</Button>
      <Button onClick={handleSave} variant="contained">Save</Button>
    </ConfigDialogActions>
  </Dialog>
}