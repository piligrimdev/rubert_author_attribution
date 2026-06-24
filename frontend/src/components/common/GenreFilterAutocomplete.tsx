import { useMemo } from "react";
import Autocomplete from "@mui/material/Autocomplete";
import TextField from "@mui/material/TextField";
import type { SxProps, Theme } from "@mui/material/styles";
import { useGenres } from "@/hooks/useGenres";

const ALL_GENRES_OPTION = "";

interface GenreFilterAutocompleteProps {
  value: string;
  onChange: (value: string) => void;
  label?: string;
  size?: "small" | "medium";
  fullWidth?: boolean;
  sx?: SxProps<Theme>;
}

export default function GenreFilterAutocomplete({
  value,
  onChange,
  label = "Жанр",
  size = "small",
  fullWidth = false,
  sx,
}: GenreFilterAutocompleteProps) {
  const { data: genres = [], isLoading } = useGenres();

  const options = useMemo(() => {
    const names = [...genres].map((g) => g.name).sort((a, b) => a.localeCompare(b, "ru"));
    return [ALL_GENRES_OPTION, ...names];
  }, [genres]);

  const getOptionLabel = (option: string) =>
    option === ALL_GENRES_OPTION ? "Все жанры" : option;

  return (
    <Autocomplete
      options={options}
      value={value}
      onChange={(_, newValue) => onChange(newValue ?? ALL_GENRES_OPTION)}
      loading={isLoading}
      fullWidth={fullWidth}
      size={size}
      sx={sx}
      disableClearable
      getOptionLabel={getOptionLabel}
      isOptionEqualToValue={(option, selected) => option === selected}
      noOptionsText={isLoading ? "Загрузка…" : "Жанры не найдены"}
      renderInput={(params) => (
        <TextField {...params} label={label} placeholder="Поиск жанра…" />
      )}
    />
  );
}
