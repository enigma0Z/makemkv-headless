import { ConfigTextField } from "@/components/fields/config/ConfigTextField"

export const RippingPathsTab = () => {

  return <>
    <ConfigTextField 
      configItem={ "source" }
      label="Source"
    />
    <ConfigTextField
      configItem="destination"
      label="Destination"
    />
    <ConfigTextField
      configItem="temp_prefix"
      label="Temp Prefix"
    />
  </>
}