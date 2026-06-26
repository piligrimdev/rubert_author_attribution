import { useMemo } from "react";
import Autocomplete from "@mui/material/Autocomplete";
import TextField from "@mui/material/TextField";
import type { SxProps, Theme } from "@mui/material/styles";
import { useGenres } from "@/hooks/useGenres";
import { strings } from "@/i18n/strings";

interface GenreAutocompleteProps {
  value: string;
  onChange: (value: string) => void;
  label?: string;
  placeholder?: string;
  size?: "small" | "medium";
  fullWidth?: boolean;
  required?: boolean;
  error?: boolean;
  helperText?: string;
  disabled?: boolean;
  sx?: SxProps<Theme>;
}

export default function GenreAutocomplete({
  value,
  onChange,
  label = strings.common.genre,
  placeholder = strings.common.genreInputPlaceholder,
  size = "medium",
  fullWidth = true,
  required = false,
  error = false,
  helperText,
  disabled = false,
  sx,
}: GenreAutocompleteProps) {
  const { data: genres = [], isLoading } = useGenres();

  const options = useMemo(
    () => [...genres].map((g) => g.name).sort((a, b) => a.localeCompare(b, "ru")),
    [genres],
  );

  return (
    <Autocomplete
      options={options}
      value={value || null}
      onChange={(_, newValue) => onChange(newValue ?? "")}
      loading={isLoading}
      disabled={disabled}
      fullWidth={fullWidth}
      size={size}
      sx={sx}
      noOptionsText={
        isLoading ? strings.common.genreLoading : strings.common.genreNotFound
      }
      renderInput={(params) => (
        <TextField
          {...params}
          label={label}
          placeholder={placeholder}
          required={required}
          error={error}
          helperText={helperText}
        />
      )}
    />
  );
}
