import { useGetConfigQuery } from "@/api/v1/config/api"
import type { Config } from "@/api/v1/config/types"
import { TextField } from "@mui/material"
import { useState } from "react"

interface Props {
  formData: Partial<Config>
  setFormData: React.Dispatch<React.SetStateAction<Partial<Config>>>
}

export const AllConfigValuesTab = (props: Props) => {
  const { formData, setFormData } = props



  return <>
    <TextField fullWidth margin="normal" label="Config File" 
    value={formData.config_file} 
    onChange={(event) => setFormData((prev) => ({...prev, config_file: event.target.value})) }
    />
    <TextField fullWidth margin="normal" label="Source" 
      value={formData.source} 
      onChange={(event) => setFormData((prev) => ({...prev, source: event.target.value})) }
    />
    <TextField fullWidth margin="normal" label="Destination" 
      value={formData.destination} 
      onChange={(event) => setFormData((prev) => ({...prev, destination: event.target.value})) }
    />
    <TextField fullWidth margin="normal" label="TMDB API Token" 
      value={formData.tmdb_token} 
      onChange={(event) => setFormData((prev) => ({...prev, tmdb_token: event.target.value})) }
    />
    <TextField fullWidth margin="normal" label="Makemkvcon Path" 
      value={formData.makemkvcon_path} 
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
      value={formData.log_file}
      onChange={(event) => setFormData((prev) => ({...prev, log_file: event.target.value})) }
    />
    <TextField fullWidth margin="normal" label="Temp Prefix" 
      value={formData.temp_prefix} 
      onChange={(event) => setFormData((prev) => ({...prev, temp_prefix: event.target.value})) }
    />
    <TextField fullWidth margin="normal" label="Frontend Address" 
      value={formData.frontend} 
      onChange={(event) => setFormData((prev) => ({...prev, frontend: event.target.value})) }
    />
    <TextField fullWidth margin="normal" label="Listen Port" 
      value={formData.listen_port} 
      onChange={(event) => setFormData((prev) => ({...prev, listen_port: event.target.value})) }
    />
    {/* <TextField fullWidth margin="normal" label="UI Path" value={data?.ui_path} /> */}
  </>
}