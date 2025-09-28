import { Dialog, DialogContent, DialogTitle } from "@mui/material"
import { StatusScroller } from "./StatusScroller"

type Props = {
  open: boolean
  onClose: () => void
}

export const LogDialog = ({ open, onClose }: Props) => {
  const handleClose = () => {
    onClose()
  }

  return <Dialog 
    fullWidth 
    maxWidth={"xl"}
    open={open} 
    onClose={handleClose}
  >
    <DialogTitle>Log Messages</DialogTitle>
    <DialogContent><StatusScroller minimized={false} showMinimizeButton={false} id="modal" /></DialogContent>
  </Dialog>
}