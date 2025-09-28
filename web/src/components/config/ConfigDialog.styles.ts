import styled from "@emotion/styled"
import { Dialog, DialogActions, DialogContent, DialogTitle } from "@mui/material"

export const ConfigDialogTitle = styled(DialogTitle)(({ theme }) => ({
  display: "flex",
  justifyContent: "space-between"
}));
export const ConfigDialogContent = styled(DialogContent)(({ theme }) => ({
  paddingTop: 0,
  paddingBottom: 0
}));
export const ConfigDialogActions = styled(DialogActions)(({ theme }) => ({
  padding: "20px 24px"
}));