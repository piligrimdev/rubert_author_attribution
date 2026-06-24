import Card from "@mui/material/Card";
import CardContent from "@mui/material/CardContent";
import CardActionArea from "@mui/material/CardActionArea";
import Typography from "@mui/material/Typography";
import Chip from "@mui/material/Chip";
import Stack from "@mui/material/Stack";
import Box from "@mui/material/Box";
import IconButton from "@mui/material/IconButton";
import Tooltip from "@mui/material/Tooltip";
import AdminPanelSettingsIcon from "@mui/icons-material/AdminPanelSettings";
import DeleteOutlineIcon from "@mui/icons-material/DeleteOutline";
import { Link } from "react-router-dom";
import type { Author } from "@/types/author";
import ConfirmDialog from "@/components/common/ConfirmDialog";
import ForbiddenDialog from "@/components/common/ForbiddenDialog";
import { useCurrentUser } from "@/hooks/useCurrentUser";
import { useDeleteAuthor } from "@/hooks/useAuthors";
import { useDeleteWithDialogs } from "@/hooks/useDeleteWithDialogs";
import { canDeleteAuthor } from "@/utils/permissions";

interface AuthorCardProps {
  author: Author;
}

function formatFullName(a: Author): string {
  return [a.surname, a.name, a.last_name].filter(Boolean).join(" ");
}

export default function AuthorCard({ author }: AuthorCardProps) {
  const { data: currentUser } = useCurrentUser();
  const deleteAuthorMutation = useDeleteAuthor();
  const deletable = canDeleteAuthor(author, currentUser);

  const deleteDialog = useDeleteWithDialogs({
    deleteFn: async (target: Author) => {
      await deleteAuthorMutation.mutateAsync(target.id);
    },
    confirmTitle: "Удалить автора?",
    getConfirmMessage: (target) =>
      `Вы уверены, что хотите удалить автора «${formatFullName(target)}»? Все связанные тексты также будут удалены.`,
    forbiddenFallback: "Удалить этого автора может только администратор или пользователь, который его добавил.",
  });

  return (
    <>
      <Card sx={{ height: "100%", display: "flex", flexDirection: "column", position: "relative" }}>
        <CardActionArea
          component={Link}
          to={`/authors/${author.id}`}
          sx={{ flex: 1, alignSelf: "stretch" }}
        >
          <CardContent>
            <Typography variant="h6" gutterBottom>
              {formatFullName(author)}
            </Typography>
            {author.description ? (
              <Typography
                variant="body2"
                color="text.secondary"
                sx={{
                  mb: 1,
                  display: "-webkit-box",
                  WebkitLineClamp: 3,
                  WebkitBoxOrient: "vertical",
                  overflow: "hidden",
                  lineHeight: 1.5,
                }}
              >
                {author.description}
              </Typography>
            ) : null}
            <Stack direction="row" spacing={1} alignItems="center" flexWrap="wrap">
              {author.provided_by === null && (
                <Chip
                  icon={<AdminPanelSettingsIcon />}
                  label="Добавлен администратором"
                  size="small"
                  color="default"
                  variant="outlined"
                />
              )}
            </Stack>
          </CardContent>
        </CardActionArea>
        {deletable && (
          <Tooltip title="Удалить автора">
            <IconButton
              size="small"
              color="error"
              aria-label="Удалить автора"
              onClick={() => deleteDialog.requestDelete(author)}
              sx={{ position: "absolute", top: 8, right: 8, bgcolor: "background.paper" }}
            >
              <DeleteOutlineIcon fontSize="small" />
            </IconButton>
          </Tooltip>
        )}
        {deleteDialog.errorMessage && (
          <Box sx={{ px: 2, pb: 1 }}>
            <Typography variant="caption" color="error">
              {deleteDialog.errorMessage}
            </Typography>
          </Box>
        )}
      </Card>

      <ConfirmDialog
        open={deleteDialog.isConfirmOpen}
        title={deleteDialog.confirmTitle}
        message={deleteDialog.confirmMessage}
        isLoading={deleteDialog.isDeleting}
        onConfirm={deleteDialog.confirmDelete}
        onCancel={deleteDialog.cancelDelete}
      />
      <ForbiddenDialog
        open={deleteDialog.isForbiddenOpen}
        message={deleteDialog.forbiddenMessage ?? ""}
        onClose={deleteDialog.closeForbidden}
      />
    </>
  );
}
