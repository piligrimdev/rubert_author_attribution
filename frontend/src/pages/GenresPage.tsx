import { useMemo } from "react";
import Stack from "@mui/material/Stack";
import Paper from "@mui/material/Paper";
import Typography from "@mui/material/Typography";
import CircularProgress from "@mui/material/CircularProgress";
import Alert from "@mui/material/Alert";
import Box from "@mui/material/Box";
import Chip from "@mui/material/Chip";
import Divider from "@mui/material/Divider";
import PageTitle from "@/components/common/PageTitle";
import { useGenres } from "@/hooks/useGenres";
import { format, strings } from "@/i18n/strings";

export default function GenresPage() {
  const { data: genres, isLoading, error } = useGenres();

  const sortedGenres = useMemo(
    () =>
      [...(genres ?? [])].sort((a, b) =>
        a.name.localeCompare(b.name, "ru"),
      ),
    [genres],
  );

  return (
    <Stack spacing={2}>
      <PageTitle subtitle={strings.genres.subtitle}>
        {strings.genres.title}
      </PageTitle>

      {isLoading && (
        <Box sx={{ display: "flex", justifyContent: "center", py: 6 }}>
          <CircularProgress />
        </Box>
      )}

      {error && (
        <Alert severity="error">
          {format(strings.genres.loadError, { message: error.message })}
        </Alert>
      )}

      {genres && sortedGenres.length === 0 && (
        <Typography color="text.secondary" sx={{ py: 4, textAlign: "center" }}>
          {strings.genres.empty}
        </Typography>
      )}

      {sortedGenres.length > 0 && (
        <Paper sx={{ p: 3 }}>
          <Stack direction="row" alignItems="center" spacing={1} sx={{ mb: 2 }}>
            <Typography variant="h6">
              {format(strings.genres.count, { count: sortedGenres.length })}
            </Typography>
          </Stack>
          <Divider sx={{ mb: 2 }} />
          <Box
            sx={{
              display: "flex",
              flexWrap: "wrap",
              gap: 1,
            }}
          >
            {sortedGenres.map((genre) => (
              <Chip
                key={genre.id}
                label={genre.name}
                variant="outlined"
                sx={{ fontSize: 14 }}
              />
            ))}
          </Box>
        </Paper>
      )}
    </Stack>
  );
}
