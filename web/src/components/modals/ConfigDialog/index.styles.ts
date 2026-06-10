import { Box, DialogActions, DialogContent, DialogTitle, styled, Tabs } from "@mui/material"

export const StyledTabContent = styled(Box)(({}) => ({
  marginLeft: '1em'
}))

export const ConfigDialogTitle = styled(DialogTitle)(({ }) => ({
  display: "flex",
  justifyContent: "space-between"
}));

export const ConfigDialogContent = styled(DialogContent)(({ }) => ({
  display: "flex",
  flexDirection: "row",
  [".MuiTabs-root"]: {
    display: 'flex',
    flexBasis: '10em',
    flexGrow: 0,
    flexShrink: 0,
    
  },
}));

export const ConfigDialogActions = styled(DialogActions)(({ }) => ({
  padding: "20px 24px"
}));