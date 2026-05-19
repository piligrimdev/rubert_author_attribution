import { useRef, useState } from "react";
import { Link } from "react-router-dom";
import Stack from "@mui/material/Stack";
import Box from "@mui/material/Box";
import Button from "@mui/material/Button";
import Paper from "@mui/material/Paper";
import Typography from "@mui/material/Typography";
import Alert from "@mui/material/Alert";
import LinearProgress from "@mui/material/LinearProgress";
import List from "@mui/material/List";
import ListItem from "@mui/material/ListItem";
import ListItemText from "@mui/material/ListItemText";
import ArrowBackIcon from "@mui/icons-material/ArrowBack";
import UploadFileIcon from "@mui/icons-material/UploadFile";
import PageTitle from "@/components/common/PageTitle";
import { useCorpusImport } from "@/hooks/useCorpusImport";

function formatAxiosError(err: { message: string; response?: { data?: unknown } }): string {
  const detail = (err.response?.data as { detail?: string } | undefined)?.detail;
  if (typeof detail === "string") return detail;
  return err.message;
}

export default function ImportCorpusPage() {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [progress, setProgress] = useState<number | null>(null);

  const importMutation = useCorpusImport();

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0] ?? null;
    setSelectedFile(file);
    importMutation.reset();
    setProgress(null);
  };

  const handleSubmit = () => {
    if (!selectedFile) return;
    setProgress(0);
    importMutation.mutate({
      file: selectedFile,
      onProgress: setProgress,
    });
  };

  const isRunning = importMutation.isPending;
  const result = importMutation.data?.result;

  return (
    <Stack spacing={3}>
      <Box>
        <Button
          component={Link}
          to="/authors"
          startIcon={<ArrowBackIcon />}
          sx={{ mb: 2 }}
        >
          К списку авторов
        </Button>
        <PageTitle subtitle="Загрузите CSV с колонками author, text и source_type (жанр) для массового добавления текстов в базу">
          Импорт корпуса из CSV
        </PageTitle>
      </Box>

      <Paper sx={{ p: 3 }}>
        <Typography variant="h6" gutterBottom>
          Формат файла
        </Typography>
        <Typography variant="body2" color="text.secondary" paragraph>
          Файл должен быть в кодировке UTF-8, расширение <strong>.csv</strong>.
          Обязательные колонки:
        </Typography>
        <List dense disablePadding sx={{ mb: 2 }}>
          <ListItem disableGutters>
            <ListItemText
              primary="author"
              secondary="Имя автора (как в базе или новое — будет создан)"
            />
          </ListItem>
          <ListItem disableGutters>
            <ListItemText primary="text" secondary="Текст фрагмента" />
          </ListItem>
          <ListItem disableGutters>
            <ListItemText
              primary="source_type"
              secondary="Жанр / тип источника (например: prose, poetry, social)"
            />
          </ListItem>
        </List>

        <Stack spacing={2}>
          <input
            ref={fileInputRef}
            type="file"
            accept=".csv,text/csv"
            hidden
            onChange={handleFileChange}
          />
          <Box sx={{ display: "flex", flexWrap: "wrap", gap: 1, alignItems: "center" }}>
            <Button
              variant="outlined"
              onClick={() => fileInputRef.current?.click()}
              disabled={isRunning}
            >
              Выбрать файл
            </Button>
            {selectedFile && (
              <Typography variant="body2" color="text.secondary">
                {selectedFile.name} ({(selectedFile.size / 1024).toFixed(1)} КБ)
              </Typography>
            )}
          </Box>

          <Button
            variant="contained"
            size="large"
            startIcon={<UploadFileIcon />}
            disabled={!selectedFile || isRunning}
            loading={isRunning}
            onClick={handleSubmit}
            sx={{ alignSelf: "flex-start" }}
          >
            Загрузить и импортировать
          </Button>
        </Stack>
      </Paper>

      {isRunning && progress !== null && (
        <Paper sx={{ p: 2 }}>
          <Typography variant="body2" color="text.secondary" gutterBottom>
            Импорт выполняется… {Math.round(progress)}%
          </Typography>
          <LinearProgress variant="determinate" value={progress} />
        </Paper>
      )}

      {importMutation.error && (
        <Alert severity="error">
          {formatAxiosError(importMutation.error)}
        </Alert>
      )}

      {importMutation.isSuccess && result && (
        <Alert severity="success">
          Импорт завершён: добавлено <strong>{result.added}</strong> фрагментов,
          пропущено пустых — {result.skipped_empty}, ошибок — {result.errors}.
        </Alert>
      )}
    </Stack>
  );
}
