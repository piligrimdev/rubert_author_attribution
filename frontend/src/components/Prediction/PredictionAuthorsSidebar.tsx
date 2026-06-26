import { useMemo, useState } from "react";
import Paper from "@mui/material/Paper";
import Typography from "@mui/material/Typography";
import TextField from "@mui/material/TextField";
import InputAdornment from "@mui/material/InputAdornment";
import List from "@mui/material/List";
import ListItem from "@mui/material/ListItem";
import ListItemButton from "@mui/material/ListItemButton";
import ListItemIcon from "@mui/material/ListItemIcon";
import ListItemText from "@mui/material/ListItemText";
import Checkbox from "@mui/material/Checkbox";
import Box from "@mui/material/Box";
import Button from "@mui/material/Button";
import Stack from "@mui/material/Stack";
import CircularProgress from "@mui/material/CircularProgress";
import SearchIcon from "@mui/icons-material/Search";
import Chip from "@mui/material/Chip";
import FormControl from "@mui/material/FormControl";
import InputLabel from "@mui/material/InputLabel";
import Select from "@mui/material/Select";
import MenuItem from "@mui/material/MenuItem";
import type { Author } from "@/types/author";
import { formatAuthorLabel } from "@/components/StyleText/authorLabel";
import {
  authorMatchesGenre,
  authorMatchesProvidedBy,
  authorMatchesQuery,
  buildAuthorGenresMap,
  type ProvidedByFilter,
} from "@/utils/authorFilter";
import { useTexts } from "@/hooks/useTexts";
import { useCurrentUser } from "@/hooks/useCurrentUser";
import GenreFilterAutocomplete from "@/components/common/GenreFilterAutocomplete";
import { format, strings } from "@/i18n/strings";

interface PredictionAuthorsSidebarProps {
  authors: Author[];
  selectedIds: string[];
  onSelectionChange: (ids: string[]) => void;
  isLoading: boolean;
}

export default function PredictionAuthorsSidebar({
  authors,
  selectedIds,
  onSelectionChange,
  isLoading,
}: PredictionAuthorsSidebarProps) {
  const [search, setSearch] = useState("");
  const [genre, setGenre] = useState("");
  const [providedBy, setProvidedBy] = useState<ProvidedByFilter>("all");
  const { data: currentUser } = useCurrentUser();
  const currentUserId = currentUser?.user_id ?? null;
  const { data: texts = [] } = useTexts();

  const genresMap = useMemo(() => buildAuthorGenresMap(texts), [texts]);

  const filtered = useMemo(
    () =>
      authors.filter(
        (author) =>
          authorMatchesQuery(author, search) &&
          authorMatchesGenre(author.id, genre, genresMap) &&
          authorMatchesProvidedBy(author, providedBy, currentUserId),
      ),
    [authors, search, genre, genresMap, providedBy, currentUserId],
  );

  const toggleId = (id: string) => {
    onSelectionChange(
      selectedIds.includes(id)
        ? selectedIds.filter((x) => x !== id)
        : [...selectedIds, id],
    );
  };

  const handleClearSelection = () => onSelectionChange([]);

  const handleSelectFiltered = () => {
    const next = new Set(selectedIds);
    filtered.forEach((a) => next.add(a.id));
    onSelectionChange([...next]);
  };

  if (isLoading) {
    return (
      <Paper
        sx={{
          width: { xs: "100%", md: 300 },
          flexShrink: 0,
          p: 2,
          display: "flex",
          alignItems: "center",
          gap: 1,
        }}
      >
        <CircularProgress size={22} />
        <Typography variant="body2" color="text.secondary">
          {strings.common.loadingAuthors}
        </Typography>
      </Paper>
    );
  }

  const hasSelection = selectedIds.length > 0;

  return (
    <Paper
      sx={{
        width: { xs: "100%", md: 300 },
        flexShrink: 0,
        display: "flex",
        flexDirection: "column",
        alignSelf: "flex-start",
        position: "sticky",
        top: 24,
        maxHeight: "calc(100vh - 120px)",
        overflow: "hidden",
      }}
    >
      <Box sx={{ p: 2, pb: 1 }}>
        <Typography variant="subtitle1" fontWeight={600} gutterBottom>
          {strings.attribution.sidebarTitle}
        </Typography>

        <Box
          sx={{
            mb: 1.5,
            p: 1.5,
            borderRadius: 1,
            border: 1,
            borderColor: "divider",
            bgcolor: "action.hover",
          }}
        >
          <Stack direction="row" spacing={1} flexWrap="wrap" useFlexGap sx={{ mb: 1 }}>
            <Chip
              label={format(strings.attribution.sidebarSelectionCount, {
                selected: selectedIds.length,
              })}
              size="small"
              color={hasSelection ? "primary" : "default"}
              sx={{ fontWeight: 700 }}
            />
            <Chip
              label={format(strings.attribution.sidebarFilteredCount, {
                filtered: filtered.length,
                total: authors.length,
              })}
              size="small"
              variant="outlined"
              sx={{ fontWeight: 600 }}
            />
          </Stack>
          <Typography variant="body2" fontWeight={600} color="text.primary" sx={{ lineHeight: 1.45 }}>
            {hasSelection
              ? strings.attribution.sidebarWithSelectionHint
              : strings.attribution.sidebarNoSelectionHint}
          </Typography>
        </Box>

        <Stack spacing={1}>
          <TextField
            size="small"
            fullWidth
            placeholder={strings.common.searchByNamePlaceholder}
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            slotProps={{
              input: {
                startAdornment: (
                  <InputAdornment position="start">
                    <SearchIcon fontSize="small" color="action" />
                  </InputAdornment>
                ),
              },
            }}
          />
          <GenreFilterAutocomplete
            value={genre}
            onChange={setGenre}
            fullWidth
          />
          <FormControl size="small" fullWidth>
            <InputLabel id="predict-authors-provided-by-label">
              {strings.authors.providedBy}
            </InputLabel>
            <Select
              labelId="predict-authors-provided-by-label"
              label={strings.authors.providedBy}
              value={providedBy}
              onChange={(e) => setProvidedBy(e.target.value as ProvidedByFilter)}
            >
              <MenuItem value="all">{strings.authors.providedByAll}</MenuItem>
              <MenuItem value="admin">{strings.authors.providedByAdmin}</MenuItem>
              <MenuItem value="mine">{strings.authors.providedByMine}</MenuItem>
            </Select>
          </FormControl>
        </Stack>
        <Stack direction="row" spacing={1} sx={{ mt: 1 }} flexWrap="wrap" useFlexGap>
          <Button size="small" onClick={handleClearSelection} disabled={selectedIds.length === 0}>
            {strings.attribution.clearSelection}
          </Button>
          <Button
            size="small"
            onClick={handleSelectFiltered}
            disabled={filtered.length === 0}
          >
            {strings.attribution.selectAllInList}
          </Button>
        </Stack>
      </Box>

      <List
        dense
        sx={{
          flex: 1,
          overflow: "auto",
          py: 0,
          borderTop: 1,
          borderColor: "divider",
        }}
      >
        {filtered.length === 0 ? (
          <ListItem>
            <ListItemText
              primary={strings.attribution.noAuthorsFound}
              secondary={strings.attribution.changeFilters}
              secondaryTypographyProps={{ color: "text.secondary" }}
            />
          </ListItem>
        ) : (
          filtered.map((author) => {
            const labelId = `predict-author-${author.id}`;
            return (
              <ListItem key={author.id} disablePadding>
                <ListItemButton onClick={() => toggleId(author.id)} dense>
                  <ListItemIcon sx={{ minWidth: 40 }}>
                    <Checkbox
                      edge="start"
                      checked={selectedIds.includes(author.id)}
                      tabIndex={-1}
                      disableRipple
                      inputProps={{ "aria-labelledby": labelId }}
                    />
                  </ListItemIcon>
                  <ListItemText
                    id={labelId}
                    primary={formatAuthorLabel(author)}
                    secondary={author.description?.trim() || undefined}
                    secondaryTypographyProps={{
                      sx: {
                        display: "-webkit-box",
                        WebkitLineClamp: 2,
                        WebkitBoxOrient: "vertical",
                        overflow: "hidden",
                        lineHeight: 1.35,
                      },
                    }}
                  />
                </ListItemButton>
              </ListItem>
            );
          })
        )}
      </List>
    </Paper>
  );
}
