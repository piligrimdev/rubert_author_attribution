import { useParams, Link } from "react-router-dom";
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
import { useAuthors } from "@/hooks/useAuthors";
import { useTextsByAuthor, useAddText } from "@/hooks/useTexts";
import AddTextForm from "@/components/Authors/AddTextForm";
import AuthorMetricsPanel from "@/components/Authors/metrics/AuthorMetricsPanel";
import type { Author } from "@/types/author";

function formatFullName(a: Author): string {
  return [a.surname, a.name, a.last_name].filter(Boolean).join(" ");
}

export default function AuthorDetailPage() {
  const { id } = useParams<{ id: string }>();
  const { data: authors, isLoading: authorsLoading } = useAuthors();
  const {
    data: texts,
    isLoading: textsLoading,
    error: textsError,
  } = useTextsByAuthor(id);
  const addTextMutation = useAddText();

  const author = authors?.find((a) => a.id === id);
  const isAdmin = author?.provided_by === null;

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
          <Typography
            variant="h4"
            sx={{ fontFamily: "'Playfair Display', serif" }}
          >
            {formatFullName(author)}
          </Typography>
          <Stack direction="row" spacing={1}>
            {isAdmin && (
              <Chip
                icon={<AdminPanelSettingsIcon />}
                label="Добавлен администратором"
                size="small"
                variant="outlined"
              />
            )}
          </Stack>
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

      <AuthorMetricsPanel authorId={author.id} textCount={texts?.length ?? 0} />

      {/* Texts section */}
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
          <Typography
            color="text.secondary"
            sx={{ py: 2, textAlign: "center" }}
          >
            У автора пока нет текстов.
          </Typography>
        )}

        {texts && texts.length > 0 && (
          <Stack spacing={2}>
            {texts.map((t) => (
              <Paper key={t.text_id} variant="outlined" sx={{ p: 2 }}>
                <Stack
                  direction="row"
                  justifyContent="space-between"
                  alignItems="center"
                  sx={{ mb: 1 }}
                >
                  <Chip label={t.genre} size="small" variant="outlined" />
                </Stack>
                <Typography
                  variant="body2"
                  sx={{
                    whiteSpace: "pre-line",
                    maxHeight: 200,
                    overflow: "auto",
                    lineHeight: 1.6,
                  }}
                >
                  {t.text}
                </Typography>
              </Paper>
            ))}
          </Stack>
        )}
      </Paper>

      {/* Add text form */}
      {addTextMutation.error && (
        <Alert severity="error">
          Не удалось добавить текст: {addTextMutation.error.message}
        </Alert>
      )}
      {addTextMutation.isSuccess && (
        <Alert severity="success">Текст успешно добавлен!</Alert>
      )}
      <AddTextForm
        onSubmit={handleAddText}
        isLoading={addTextMutation.isPending}
      />
    </Stack>
  );
}
