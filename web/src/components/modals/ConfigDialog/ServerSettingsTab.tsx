import { ConfigTextField } from "@/components/fields/config/ConfigTextField"

export const ServerSettingsTab = () => {

  return <>
    <ConfigTextField 
      configItem={ "config_file" }
      label="Config File"
    />
    <ConfigTextField
      configItem="log_file"
      label="Log File"
    />
    <ConfigTextField
      configItem="frontend"
      label="Frontend Address (include http://)"
    />
    <ConfigTextField
      configItem="listen_port"
      label="Listen Port"
    />
  </>
}