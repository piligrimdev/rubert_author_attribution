import { useState } from "react";
import { useParams, Link, useNavigate } from "react-router-dom";
import Stack from "@mui/material/Stack";
import Paper from "@mui/material/Paper";
import Typography from "@mui/material/Typography";
import CircularProgress from "@mui/material/CircularProgress";
import Alert from "@mui/material/Alert";
import Box from "@mui/material/Box";
import Chip from "@mui/material/Chip";
import Divider from "@mui/material/Divider";
import Button from "@mui/material/Button";
import ArrowBackIcon from "@mui/icons-material/ArrowBack";
import AdminPanelSettingsIcon from "@mui/icons-material/AdminPanelSettings";
import BarChartIcon from "@mui/icons-material/BarChart";
import ArticleIcon from "@mui/icons-material/Article";
import DeleteOutlineIcon from "@mui/icons-material/DeleteOutline";
import EditOutlinedIcon from "@mui/icons-material/EditOutlined";
import { useAuthors, useDeleteAuthor, useEditAuthor } from "@/hooks/useAuthors";
import { useTextsByAuthor, useAddText, useDeleteText } from "@/hooks/useTexts";
import { useCurrentUser } from "@/hooks/useCurrentUser";
import { useDeleteWithDialogs } from "@/hooks/useDeleteWithDialogs";
import AddTextForm from "@/components/Authors/AddTextForm";
import EditAuthorForm from "@/components/Authors/EditAuthorForm";
import AuthorTextItem from "@/components/Authors/AuthorTextItem";
import AuthorMetricsPanel from "@/components/Authors/metrics/AuthorMetricsPanel";
import ConfirmDialog from "@/components/common/ConfirmDialog";
import ForbiddenDialog from "@/components/common/ForbiddenDialog";
import { canDeleteAuthor, canEditAuthor } from "@/utils/permissions";
import { getApiErrorDetail, isForbiddenError } from "@/utils/apiError";
import type { Author, EditAuthorRequest } from "@/types/author";
import type { TextItem } from "@/types/text";

function formatFullName(a: Author): string {
  return [a.surname, a.name, a.last_name].filter(Boolean).join(" ");
}

export default function AuthorDetailPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { data: authors, isLoading: authorsLoading } = useAuthors();
  const { data: currentUser } = useCurrentUser();
  const {
    data: texts,
    isLoading: textsLoading,
    error: textsError,
  } = useTextsByAuthor(id);
  const addTextMutation = useAddText();
  const deleteAuthorMutation = useDeleteAuthor();
  const deleteTextMutation = useDeleteText();
  const editAuthorMutation = useEditAuthor();

  const [isEditingAuthor, setIsEditingAuthor] = useState(false);
  const [editAuthorError, setEditAuthorError] = useState<string | null>(null);
  const [editAuthorForbidden, setEditAuthorForbidden] = useState<string | null>(null);

  const author = authors?.find((a) => a.id === id);
  const canDeleteThisAuthor = author ? canDeleteAuthor(author, currentUser) : false;
  const canEditThisAuthor = author ? canEditAuthor(author, currentUser) : false;

  const deleteAuthorDialog = useDeleteWithDialogs({
    deleteFn: async (target: Author) => {
      await deleteAuthorMutation.mutateAsync(target.id);
    },
    confirmTitle: "Удалить автора?",
    getConfirmMessage: (target) =>
      `Вы уверены, что хотите удалить автора «${formatFullName(target)}»? Все связанные тексты также будут удалены.`,
    forbiddenFallback:
      "Удалить этого автора может только администратор или пользователь, который его добавил.",
    onSuccess: () => navigate("/authors"),
  });

  const deleteTextDialog = useDeleteWithDialogs({
    deleteFn: async (target: TextItem) => {
      await deleteTextMutation.mutateAsync({
        textId: target.text_id,
        authorId: target.author_id,
      });
    },
    confirmTitle: "Удалить текст?",
    getConfirmMessage: () =>
      "Вы уверены, что хотите удалить этот текст? Это действие нельзя отменить.",
    forbiddenFallback:
      "Удалить этот текст может только администратор или пользователь, который его добавил.",
  });

  if (authorsLoading) {
    return (
      <Box sx={{ display: "flex", justifyContent: "center", py: 6 }}>
        <CircularProgress />
      </Box>
    );
  }

  if (!author) {
    return (
      <Alert severity="warning">
        Автор не найден.{" "}
        <Typography component={Link} to="/authors" color="primary">
          Вернуться к списку
        </Typography>
      </Alert>
    );
  }

  const handleAddText = (data: { text: string; genre_name: string }) => {
    addTextMutation.mutate({
      text: data.text,
      author_id: author.id,
      genre_name: data.genre_name,
    });
  };

  const handleEditAuthor = async (data: EditAuthorRequest) => {
    if (Object.keys(data).length === 0) {
      setEditAuthorError("Нет изменений для сохранения");
      return;
    }

    setEditAuthorError(null);
    try {
      await editAuthorMutation.mutateAsync({
        authorId: author.id,
        data,
      });
      setIsEditingAuthor(false);
    } catch (err) {
      if (isForbiddenError(err)) {
        setIsEditingAuthor(false);
        setEditAuthorForbidden(
          getApiErrorDetail(
            err,
            "Редактировать этого автора может только администратор или пользователь, который его добавил.",
          ),
        );
      } else {
        setEditAuthorError(getApiErrorDetail(err, "Не удалось сохранить изменения"));
      }
    }
  };

  return (
    <Stack spacing={3}>
      <Button
        component={Link}
        to="/authors"
        startIcon={<ArrowBackIcon />}
        sx={{ alignSelf: "flex-start", color: "text.secondary" }}
      >
        К списку авторов
      </Button>

      <Paper sx={{ p: 3 }}>
        <Stack spacing={1}>
          <Stack
            direction="row"
            justifyContent="space-between"
            alignItems="flex-start"
            spacing={2}
          >
            {!isEditingAuthor ? (
              <Typography
                variant="h4"
                sx={{ fontFamily: "'Playfair Display', serif" }}
              >
                {formatFullName(author)}
              </Typography>
            ) : (
              <Box sx={{ flex: 1 }} />
            )}
            <Stack direction="row" spacing={1} flexWrap="wrap" useFlexGap>
              {canEditThisAuthor && !isEditingAuthor && (
                <Button
                  variant="outlined"
                  startIcon={<EditOutlinedIcon />}
                  onClick={() => {
                    setIsEditingAuthor(true);
                    setEditAuthorError(null);
                  }}
                >
                  Редактировать
                </Button>
              )}
              {canDeleteThisAuthor && !isEditingAuthor && (
                <Button
                  color="error"
                  variant="outlined"
                  startIcon={<DeleteOutlineIcon />}
                  onClick={() => deleteAuthorDialog.requestDelete(author)}
                >
                  Удалить автора
                </Button>
              )}
            </Stack>
          </Stack>

          {isEditingAuthor ? (
            <EditAuthorForm
              author={author}
              onSubmit={handleEditAuthor}
              onCancel={() => {
                setIsEditingAuthor(false);
                setEditAuthorError(null);
              }}
              isLoading={editAuthorMutation.isPending}
            />
          ) : (
            <>
              <Stack direction="row" spacing={1}>
                {author.provided_by === null && (
                  <Chip
                    icon={<AdminPanelSettingsIcon />}
                    label="Добавлен администратором"
                    size="small"
                    variant="outlined"
                  />
                )}
              </Stack>
              {author.description ? (
                <Typography
                  variant="body1"
                  color="text.secondary"
                  sx={{ mt: 1, whiteSpace: "pre-line", lineHeight: 1.7 }}
                >
                  {author.description}
                </Typography>
              ) : null}
            </>
          )}

          {editAuthorError && (
            <Alert severity="error" sx={{ mt: 1 }}>
              {editAuthorError}
            </Alert>
          )}
          {deleteAuthorDialog.errorMessage && (
            <Alert severity="error" sx={{ mt: 1 }}>
              {deleteAuthorDialog.errorMessage}
            </Alert>
          )}
        </Stack>
      </Paper>

      <Paper sx={{ p: 3 }}>
        <Stack direction="row" alignItems="center" spacing={1} sx={{ mb: 2 }}>
          <BarChartIcon color="primary" />
          <Typography variant="h6">Статистика автора</Typography>
        </Stack>
        <Divider sx={{ mb: 2 }} />
        <Box
          sx={{
            display: "grid",
            gridTemplateColumns: "repeat(auto-fit, minmax(180px, 1fr))",
            gap: 2,
          }}
        >
          <Paper variant="outlined" sx={{ p: 2, textAlign: "center" }}>
            <Typography variant="h5" color="primary" fontWeight={700}>
              {texts?.length ?? "—"}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Количество текстов в базе
            </Typography>
          </Paper>
        </Box>
      </Paper>

      <AuthorMetricsPanel
        authorId={author.id}
        textCount={texts?.length ?? 0}
        authorsForCompare={authors ?? []}
      />

      <Paper sx={{ p: 3 }}>
        <Stack direction="row" alignItems="center" spacing={1} sx={{ mb: 2 }}>
          <ArticleIcon color="primary" />
          <Typography variant="h6">Тексты автора</Typography>
        </Stack>
        <Divider sx={{ mb: 2 }} />

        {textsLoading && (
          <Box sx={{ display: "flex", justifyContent: "center", py: 4 }}>
            <CircularProgress size={32} />
          </Box>
        )}

        {textsError && (
          <Alert severity="error" sx={{ mb: 2 }}>
            Не удалось загрузить тексты: {textsError.message}
          </Alert>
        )}

        {texts && !texts.length && (
          <Typography color="text.secondary" sx={{ py: 2, textAlign: "center" }}>
            У автора пока нет текстов.
          </Typography>
        )}

        {texts && texts.length > 0 && (
          <Stack spacing={2}>
            {texts.map((t) => (
              <AuthorTextItem
                key={t.text_id}
                text={t}
                currentUser={currentUser}
                onDelete={(text) => deleteTextDialog.requestDelete(text)}
              />
            ))}
          </Stack>
        )}

        {deleteTextDialog.errorMessage && (
          <Alert severity="error" sx={{ mt: 2 }}>
            {deleteTextDialog.errorMessage}
          </Alert>
        )}
      </Paper>

      {addTextMutation.error && (
        <Alert severity="error">
          Не удалось добавить текст: {addTextMutation.error.message}
        </Alert>
      )}
      {addTextMutation.isSuccess && (
        <Alert severity="success">Текст успешно добавлен!</Alert>
      )}
      <AddTextForm onSubmit={handleAddText} isLoading={addTextMutation.isPending} />

      <ConfirmDialog
        open={deleteAuthorDialog.isConfirmOpen}
        title={deleteAuthorDialog.confirmTitle}
        message={deleteAuthorDialog.confirmMessage}
        isLoading={deleteAuthorDialog.isDeleting}
        onConfirm={deleteAuthorDialog.confirmDelete}
        onCancel={deleteAuthorDialog.cancelDelete}
      />
      <ForbiddenDialog
        open={deleteAuthorDialog.isForbiddenOpen}
        message={deleteAuthorDialog.forbiddenMessage ?? ""}
        onClose={deleteAuthorDialog.closeForbidden}
      />

      <ConfirmDialog
        open={deleteTextDialog.isConfirmOpen}
        title={deleteTextDialog.confirmTitle}
        message={deleteTextDialog.confirmMessage}
        isLoading={deleteTextDialog.isDeleting}
        onConfirm={deleteTextDialog.confirmDelete}
        onCancel={deleteTextDialog.cancelDelete}
      />
      <ForbiddenDialog
        open={deleteTextDialog.isForbiddenOpen}
        message={deleteTextDialog.forbiddenMessage ?? ""}
        onClose={deleteTextDialog.closeForbidden}
      />
      <ForbiddenDialog
        open={editAuthorForbidden !== null}
        message={editAuthorForbidden ?? ""}
        onClose={() => setEditAuthorForbidden(null)}
      />
    </Stack>
  );
}
