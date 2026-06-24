import TextField from "@mui/material/TextField";
import InputAdornment from "@mui/material/InputAdornment";
import FormControl from "@mui/material/FormControl";
import InputLabel from "@mui/material/InputLabel";
import Select from "@mui/material/Select";
import MenuItem from "@mui/material/MenuItem";
import Stack from "@mui/material/Stack";
import SearchIcon from "@mui/icons-material/Search";
import GenreFilterAutocomplete from "@/components/common/GenreFilterAutocomplete";
import type { ProvidedByFilter } from "@/utils/authorFilter";

interface AuthorsFiltersProps {
  search: string;
  onSearchChange: (value: string) => void;
  genre: string;
  onGenreChange: (value: string) => void;
  providedBy: ProvidedByFilter;
  onProvidedByChange: (value: ProvidedByFilter) => void;
}

export default function AuthorsFilters({
  search,
  onSearchChange,
  genre,
  onGenreChange,
  providedBy,
  onProvidedByChange,
}: AuthorsFiltersProps) {
  return (
    <Stack
      direction={{ xs: "column", sm: "row" }}
      spacing={2}
      useFlexGap
      flexWrap="wrap"
    >
      <TextField
        size="small"
        placeholder="Поиск по имени или фамилии…"
        value={search}
        onChange={(e) => onSearchChange(e.target.value)}
        sx={{ flex: { sm: "1 1 240px" }, minWidth: 200 }}
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
        onChange={onGenreChange}
        sx={{ minWidth: 180, flex: { sm: "0 1 220px" } }}
      />

      <FormControl size="small" sx={{ minWidth: 220 }}>
        <InputLabel id="authors-provided-by-filter-label">Кто добавил</InputLabel>
        <Select
          labelId="authors-provided-by-filter-label"
          label="Кто добавил"
          value={providedBy}
          onChange={(e) => onProvidedByChange(e.target.value as ProvidedByFilter)}
        >
          <MenuItem value="all">Все</MenuItem>
          <MenuItem value="admin">Администратор</MenuItem>
          <MenuItem value="mine">Я</MenuItem>
        </Select>
      </FormControl>
    </Stack>
  );
}
