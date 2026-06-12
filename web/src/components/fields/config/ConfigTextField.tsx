import { useAppDispatch, useAppSelector } from "@/api";
import { useGetConfigQuery } from "@/api/v1/config/api";
import { configActions } from "@/api/v1/config/store"
import type { Config } from "@/api/v1/config/types";
import { Box, CircularProgress, TextField } from "@mui/material"
import type React from "react"

interface Props {
  configItem: keyof Config
  label?: string
}

export const ConfigTextField = ({configItem, label}: Props) => {

  const dispatch = useAppDispatch()

  const fieldValue = useAppSelector((store) => store.config[configItem])
  const { data } = useGetConfigQuery()
  const apiValue = data?.[configItem]

  type FieldOnChange = React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>

  const handleFieldUpdate = ({ target: { value } }: FieldOnChange) => {
    dispatch(configActions.updateConfig({[configItem]: value}))
  }

  return <Box sx={{ display: "flex", flexDirection: "row", alignItems: "center", verticalAlign: "center"}}>
    <TextField fullWidth margin="normal" label={label ?? configItem}
        value={fieldValue} 
        onChange={handleFieldUpdate}
    />
    <CircularProgress sx={{ 
      marginLeft: "1em", 
      position: "absolute", 
      right: 48,
      display: apiValue === fieldValue ? "none" : "inherit",
    }} size={32} />
  </Box>
}