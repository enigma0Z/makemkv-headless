import styled from "@emotion/styled"
import { DialogActions, DialogContent, DialogTitle } from "@mui/material"

export const ConfigDialogTitle = styled(DialogTitle)(({ }) => ({
  display: "flex",
  justifyContent: "space-between"
}));
export const ConfigDialogContent = styled(DialogContent)(({ }) => ({
  paddingTop: 0,
  paddingBottom: 0
}));
export const ConfigDialogActions = styled(DialogActions)(({ }) => ({
  padding: "20px 24px"
}));