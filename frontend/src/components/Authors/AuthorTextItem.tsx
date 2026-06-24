import { useEffect, useState } from "react";
import Paper from "@mui/material/Paper";
import Stack from "@mui/material/Stack";
import Typography from "@mui/material/Typography";
import Chip from "@mui/material/Chip";
import TextField from "@mui/material/TextField";
import Button from "@mui/material/Button";
import IconButton from "@mui/material/IconButton";
import Tooltip from "@mui/material/Tooltip";
import Alert from "@mui/material/Alert";
import EditOutlinedIcon from "@mui/icons-material/EditOutlined";
import DeleteOutlineIcon from "@mui/icons-material/DeleteOutline";
import SaveIcon from "@mui/icons-material/Save";
import CloseIcon from "@mui/icons-material/Close";
import ForbiddenDialog from "@/components/common/ForbiddenDialog";
import { useEditText } from "@/hooks/useTexts";
import { canDeleteText, canEditText } from "@/utils/permissions";
import { getApiErrorDetail, isForbiddenError } from "@/utils/apiError";
import type { CurrentUser } from "@/types/auth";
import type { TextItem } from "@/types/text";

interface AuthorTextItemProps {
  text: TextItem;
  currentUser: CurrentUser | undefined;
  onDelete: (text: TextItem) => void;
}

export default function AuthorTextItem({
  text,
  currentUser,
  onDelete,
}: AuthorTextItemProps) {
  const [isEditing, setIsEditing] = useState(false);
  const [draft, setDraft] = useState(text.text);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [forbiddenMessage, setForbiddenMessage] = useState<string | null>(null);
  const editTextMutation = useEditText();

  const editable = canEditText(text, currentUser);
  const deletable = canDeleteText(text, currentUser);

  useEffect(() => {
    if (!isEditing) setDraft(text.text);
  }, [text.text, isEditing]);

  const handleCancel = () => {
    setDraft(text.text);
    setIsEditing(false);
    setErrorMessage(null);
  };

  const handleSave = async () => {
    const trimmed = draft.trim();
    if (!trimmed) {
      setErrorMessage("Текст не может быть пустым");
      return;
    }
    if (trimmed === text.text) {
      setIsEditing(false);
      setErrorMessage(null);
      return;
    }

    setErrorMessage(null);
    try {
      await editTextMutation.mutateAsync({
        textId: text.text_id,
        authorId: text.author_id,
        data: { text: trimmed },
      });
      setIsEditing(false);
    } catch (err) {
      if (isForbiddenError(err)) {
        setIsEditing(false);
        setForbiddenMessage(
          getApiErrorDetail(
            err,
            "Редактировать этот текст может только администратор или пользователь, который его добавил.",
          ),
        );
      } else {
        setErrorMessage(getApiErrorDetail(err, "Не удалось сохранить текст"));
      }
    }
  };

  return (
    <>
      <Paper variant="outlined" sx={{ p: 2 }}>
        <Stack
          direction="row"
          justifyContent="space-between"
          alignItems="center"
          sx={{ mb: 1 }}
        >
          <Chip label={text.genre} size="small" variant="outlined" />
          <Stack direction="row" spacing={0.5}>
            {editable && !isEditing && (
              <Tooltip title="Редактировать текст">
                <IconButton
                  size="small"
                  aria-label="Редактировать текст"
                  onClick={() => {
                    setIsEditing(true);
                    setErrorMessage(null);
                  }}
                >
                  <EditOutlinedIcon fontSize="small" />
                </IconButton>
              </Tooltip>
            )}
            {deletable && !isEditing && (
              <Tooltip title="Удалить текст">
                <IconButton
                  size="small"
                  color="error"
                  aria-label="Удалить текст"
                  onClick={() => onDelete(text)}
                >
                  <DeleteOutlineIcon fontSize="small" />
                </IconButton>
              </Tooltip>
            )}
          </Stack>
        </Stack>

        {isEditing ? (
          <Stack spacing={1.5}>
            <TextField
              value={draft}
              onChange={(e) => setDraft(e.target.value)}
              multiline
              minRows={4}
              fullWidth
              disabled={editTextMutation.isPending}
            />
            <Stack direction="row" spacing={1}>
              <Button
                variant="contained"
                size="small"
                startIcon={<SaveIcon />}
                onClick={handleSave}
                disabled={editTextMutation.isPending}
              >
                Сохранить
              </Button>
              <Button
                variant="outlined"
                size="small"
                startIcon={<CloseIcon />}
                onClick={handleCancel}
                disabled={editTextMutation.isPending}
              >
                Отмена
              </Button>
            </Stack>
          </Stack>
        ) : (
          <Typography
            variant="body2"
            sx={{
              whiteSpace: "pre-line",
              maxHeight: 200,
              overflow: "auto",
              lineHeight: 1.6,
            }}
          >
            {text.text}
          </Typography>
        )}

        {errorMessage && (
          <Alert severity="error" sx={{ mt: 1.5 }}>
            {errorMessage}
          </Alert>
        )}
      </Paper>

      <ForbiddenDialog
        open={forbiddenMessage !== null}
        message={forbiddenMessage ?? ""}
        onClose={() => setForbiddenMessage(null)}
      />
    </>
  );
}
