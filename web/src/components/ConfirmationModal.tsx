import { Button, Card, Dialog, DialogActions, DialogContent, DialogContentText, DialogTitle, Modal, Typography } from "@mui/material";

type Props = {
  title: string;
  message: string;
  open: boolean;
  noText?: string;
  yesText?: string;
  onClose: () => void;
  onCancel?: () => void;
  onConfirm: () => void;
}

export const ConfirmationDialog = ({
  title,
  message,
  open,
  noText = "No",
  yesText = "Yes",
  onClose, 
  onCancel = () => {}, 
  onConfirm,
}: Props) => {
  const handleCancel = () => {
    onCancel()
    onClose()
  }

  const handleConfirm = () => {
    onConfirm()
    onClose()
  }

  return <Dialog
    open={open}
    onClose={onClose}
    aria-labelledby="alert-dialog-title"
    aria-describedby="alert-dialog-description"
    maxWidth={"md"}
  >
    <DialogTitle id="alert-dialog-title">
      {title}
    </DialogTitle>
    <DialogContent>
      <DialogContentText id="alert-dialog-description">
        {message}
      </DialogContentText>
    </DialogContent>
    <DialogActions>
      <Button variant="outlined" onClick={handleCancel}>{noText}</Button>
      <Button variant="contained" onClick={handleConfirm} autoFocus>{yesText}</Button>
    </DialogActions>
  </Dialog>
  
  // <Modal
  //   open={open}  
  //   onClose={onClose}
  // >
  //   <Card>
  //     {children}
  //     <Button
  //       onClick={onCancel}
  //       variant="outlined"
  //     >
  //       {noText}
  //     </Button>
  //     <Button
  //       variant="outlined"
  //       onClick={onConfirm}
  //     >
  //       {yesText}
  //     </Button>
  //   </Card>
  // </Modal>
};