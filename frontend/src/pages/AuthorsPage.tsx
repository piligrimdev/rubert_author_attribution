import Stack from "@mui/material/Stack";
import Button from "@mui/material/Button";
import CircularProgress from "@mui/material/CircularProgress";
import Alert from "@mui/material/Alert";
import Box from "@mui/material/Box";
import Typography from "@mui/material/Typography";
import PersonAddIcon from "@mui/icons-material/PersonAdd";
import UploadFileIcon from "@mui/icons-material/UploadFile";
import { Link } from "react-router-dom";
import PageTitle from "@/components/common/PageTitle";
import AuthorsGrid from "@/components/Authors/AuthorsGrid";
import { useAuthors } from "@/hooks/useAuthors";

export default function AuthorsPage() {
  const { data: authors, isLoading, error } = useAuthors();

  return (
    <Stack spacing={2}>
      <Box
        sx={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "flex-start",
        }}
      >
        <PageTitle subtitle="Список авторов в базе данных. Стилистические метрики (графики) доступны на странице выбранного автора.">
          Авторы
        </PageTitle>
        <Stack direction="row" spacing={1} sx={{ flexShrink: 0 }}>
          <Button
            component={Link}
            to="/authors/import"
            variant="outlined"
            startIcon={<UploadFileIcon />}
          >
            Импорт CSV
          </Button>
          <Button
            component={Link}
            to="/authors/new"
            variant="contained"
            startIcon={<PersonAddIcon />}
          >
            Добавить автора
          </Button>
        </Stack>
      </Box>

      {isLoading && (
        <Box sx={{ display: "flex", justifyContent: "center", py: 6 }}>
          <CircularProgress />
        </Box>
      )}

      {error && (
        <Alert severity="error">
          Не удалось загрузить список авторов: {error.message}
        </Alert>
      )}

      {authors && !authors.length && (
        <Typography color="text.secondary" sx={{ py: 4, textAlign: "center" }}>
          Авторов пока нет. Добавьте первого!
        </Typography>
      )}

      {authors && authors.length > 0 && <AuthorsGrid authors={authors} />}
    </Stack>
  );
}
