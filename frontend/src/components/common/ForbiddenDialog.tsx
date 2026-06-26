import Dialog from "@mui/material/Dialog";
import DialogTitle from "@mui/material/DialogTitle";
import DialogContent from "@mui/material/DialogContent";
import DialogContentText from "@mui/material/DialogContentText";
import DialogActions from "@mui/material/DialogActions";
import Button from "@mui/material/Button";
import { strings } from "@/i18n/strings";

interface ForbiddenDialogProps {
  open: boolean;
  message: string;
  onClose: () => void;
}

export default function ForbiddenDialog({
  open,
  message,
  onClose,
}: ForbiddenDialogProps) {
  return (
    <Dialog open={open} onClose={onClose} maxWidth="xs" fullWidth>
      <DialogTitle>{strings.dialogs.forbiddenTitle}</DialogTitle>
      <DialogContent>
        <DialogContentText>{message}</DialogContentText>
      </DialogContent>
      <DialogActions sx={{ px: 3, pb: 2 }}>
        <Button onClick={onClose} variant="contained">
          {strings.dialogs.forbiddenOk}
        </Button>
      </DialogActions>
    </Dialog>
  );
}
