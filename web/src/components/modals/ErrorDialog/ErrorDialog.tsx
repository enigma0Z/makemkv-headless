import { Button, Dialog, IconButton, Typography } from "@mui/material";
import { ErrorDialogActions, ErrorDialogContent, ErrorDialogTitle } from "./ErrorDialog.styles";

import CloseIcon from '@mui/icons-material/Close';
import type { ApiError } from "@/api/v1/error/types";
import { useClearErrorMutation } from "@/api/v1/error/api";

type Props = {
  open: boolean;
  errorData?: ApiError;
  onClose?: () => void;
}

export const ErrorDialog = ({open, errorData, onClose = () => {}}: Props) => {

  const [clearError, _] = useClearErrorMutation()  

  const handleClose = () => {
    clearError()
    onClose()
  }

  return <Dialog onClose={handleClose} open={open} maxWidth='xl' fullWidth>
    <ErrorDialogTitle>
      <Typography variant="h4">Error</Typography>
      <IconButton onClick={handleClose}><CloseIcon /></IconButton>
    </ErrorDialogTitle>
    <ErrorDialogContent>
      <Typography variant="h6">
        {errorData?.message} @ {errorData?.path}
      </Typography>
      <Typography variant="body2">
        <pre>
          {errorData?.traceback?.join('\n')}
        </pre>
      </Typography >
    </ErrorDialogContent>
    <ErrorDialogActions>
      <Button onClick={handleClose}>OK</Button>
    </ErrorDialogActions>
  </Dialog>;
}