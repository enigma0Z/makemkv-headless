import { ConfigTextField } from "@/components/fields/config/ConfigTextField"

export const AllConfigValuesTab = () => {

  return <>
    <ConfigTextField 
      configItem={ "config_file" }
      label="Config File"
    />
    <ConfigTextField 
      configItem={ "source" }
      label="Source"
    />
    <ConfigTextField
      configItem="destination"
      label="Destination"
    />
    <ConfigTextField 
      configItem="tmdb_token"
      label="TMDB API Token"
    />
    <ConfigTextField
      configItem="makemkvcon_path"
      label="Path to makemkvcon"
    />
    {/* 
    TODO: Make this one a select with log levels
    <TextField fullWidth margin="normal" label="Log Level" 
      value={log_level}
      onChange={(event) => setFormData((prev) => ({...prev, log_level: event.target.value})) }
    /> 
    */}
    <ConfigTextField
      configItem="log_file"
      label="Log File"
    />
    <ConfigTextField
      configItem="temp_prefix"
      label="Temp Prefix"
    />
    <ConfigTextField
      configItem="frontend"
      label="Frontend Address (include http://)"
    />
    <ConfigTextField
      configItem="listen_port"
      label="Listen Port"
    />
    {/* <TextField fullWidth margin="normal" label="UI Path" value={data?.ui_path} /> */}
  </>
}