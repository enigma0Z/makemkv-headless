import styled from "@emotion/styled"
import { DialogActions, DialogContent, DialogTitle } from "@mui/material"
import { red } from "@mui/material/colors";

export const ErrorDialogTitle = styled(DialogTitle)(({ }) => ({
  display: "flex",
  justifyContent: "space-between"
}));

export const ErrorDialogContent = styled(DialogContent)(({ }) => ({
  paddingTop: 0,
  paddingBottom: 0,
  pre: {
    color: red['A200']
  }
}));

export const ErrorDialogActions = styled(DialogActions)(({ }) => ({
  padding: "20px 24px"
}));