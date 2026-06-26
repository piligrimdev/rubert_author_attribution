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
import { format, strings } from "@/i18n/strings";

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
          {strings.common.backToAuthors}
        </Button>
        <PageTitle subtitle={strings.importCorpus.subtitle}>
          {strings.importCorpus.title}
        </PageTitle>
      </Box>

      <Paper sx={{ p: 3 }}>
        <Typography variant="h6" gutterBottom>
          {strings.importCorpus.formatTitle}
        </Typography>
        <Typography variant="body2" color="text.secondary" paragraph>
          {strings.importCorpus.formatDescription}
        </Typography>
        <List dense disablePadding sx={{ mb: 2 }}>
          <ListItem disableGutters>
            <ListItemText
              primary={strings.importCorpus.columnAuthor}
              secondary={strings.importCorpus.columnAuthorHint}
            />
          </ListItem>
          <ListItem disableGutters>
            <ListItemText
              primary={strings.importCorpus.columnText}
              secondary={strings.importCorpus.columnTextHint}
            />
          </ListItem>
          <ListItem disableGutters>
            <ListItemText
              primary={strings.importCorpus.columnSourceType}
              secondary={strings.importCorpus.columnSourceTypeHint}
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
              {strings.importCorpus.selectFile}
            </Button>
            {selectedFile && (
              <Typography variant="body2" color="text.secondary">
                {format(strings.importCorpus.fileSizeKb, {
                  name: selectedFile.name,
                  size: (selectedFile.size / 1024).toFixed(1),
                })}
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
            {strings.importCorpus.upload}
          </Button>
        </Stack>
      </Paper>

      {isRunning && progress !== null && (
        <Paper sx={{ p: 2 }}>
          <Typography variant="body2" color="text.secondary" gutterBottom>
            {format(strings.importCorpus.progress, { percent: Math.round(progress) })}
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
        <Stack spacing={2}>
          <Alert severity="success">
            {format(strings.importCorpus.success, {
              added: result.added,
              skipped: result.skipped_empty,
            })}
          </Alert>
          {result.errors.length > 0 && (
            <Alert severity="warning">
              <Typography variant="body2" gutterBottom>
                {format(strings.importCorpus.errorsTitle, {
                  count: result.errors.length,
                })}
              </Typography>
              <List dense disablePadding>
                {result.errors.map((item) => (
                  <ListItem key={item.ind} disableGutters sx={{ py: 0 }}>
                    <ListItemText
                      primary={format(strings.importCorpus.errorRow, {
                        row: item.ind,
                        message: item.error,
                      })}
                      primaryTypographyProps={{ variant: "body2" }}
                    />
                  </ListItem>
                ))}
              </List>
            </Alert>
          )}
        </Stack>
      )}
    </Stack>
  );
}
