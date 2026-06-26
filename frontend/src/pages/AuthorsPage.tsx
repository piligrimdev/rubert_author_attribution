import { useMemo, useState } from "react";
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
import AuthorsFilters from "@/components/Authors/AuthorsFilters";
import { useAuthors } from "@/hooks/useAuthors";
import { useTexts } from "@/hooks/useTexts";
import { useCurrentUser } from "@/hooks/useCurrentUser";
import {
  buildAuthorGenresMap,
  filterAuthors,
  type ProvidedByFilter,
} from "@/utils/authorFilter";
import { format, strings } from "@/i18n/strings";

export default function AuthorsPage() {
  const [search, setSearch] = useState("");
  const [genre, setGenre] = useState("");
  const [providedBy, setProvidedBy] = useState<ProvidedByFilter>("all");
  const { data: currentUser } = useCurrentUser();
  const currentUserId = currentUser?.user_id ?? null;
  const { data: authors, isLoading, error } = useAuthors();
  const { data: texts = [] } = useTexts();

  const genresMap = useMemo(() => buildAuthorGenresMap(texts), [texts]);

  const filteredAuthors = useMemo(
    () =>
      filterAuthors(authors ?? [], {
        search,
        genre,
        providedBy,
        genresMap,
        currentUserId,
      }),
    [authors, search, genre, providedBy, genresMap, currentUserId],
  );

  const hasActiveFilters = search.trim() !== "" || genre !== "" || providedBy !== "all";

  return (
    <Stack spacing={2}>
      <Box
        sx={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "flex-start",
        }}
      >
        <PageTitle>{strings.authors.title}</PageTitle>
        <Stack direction="row" spacing={1} sx={{ flexShrink: 0 }}>
          <Button
            component={Link}
            to="/authors/import"
            variant="outlined"
            startIcon={<UploadFileIcon />}
          >
            {strings.authors.importCsv}
          </Button>
          <Button
            component={Link}
            to="/authors/new"
            variant="contained"
            startIcon={<PersonAddIcon />}
          >
            {strings.authors.addAuthor}
          </Button>
        </Stack>
      </Box>

      {authors && authors.length > 0 && (
        <AuthorsFilters
          search={search}
          onSearchChange={setSearch}
          genre={genre}
          onGenreChange={setGenre}
          providedBy={providedBy}
          onProvidedByChange={setProvidedBy}
        />
      )}

      {isLoading && (
        <Box sx={{ display: "flex", justifyContent: "center", py: 6 }}>
          <CircularProgress />
        </Box>
      )}

      {error && (
        <Alert severity="error">
          {format(strings.authors.loadError, { message: error.message })}
        </Alert>
      )}

      {authors && !authors.length && (
        <Typography color="text.secondary" sx={{ py: 4, textAlign: "center" }}>
          {strings.authors.empty}
        </Typography>
      )}

      {authors && authors.length > 0 && filteredAuthors.length === 0 && (
        <Typography color="text.secondary" sx={{ py: 4, textAlign: "center" }}>
          {hasActiveFilters
            ? strings.authors.emptyFiltered
            : strings.authors.empty}
        </Typography>
      )}

      {filteredAuthors.length > 0 && <AuthorsGrid authors={filteredAuthors} />}
    </Stack>
  );
}
