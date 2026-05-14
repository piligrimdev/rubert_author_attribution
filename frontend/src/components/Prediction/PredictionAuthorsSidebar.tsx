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
import FormHelperText from "@mui/material/FormHelperText";
import Box from "@mui/material/Box";
import Button from "@mui/material/Button";
import Stack from "@mui/material/Stack";
import CircularProgress from "@mui/material/CircularProgress";
import SearchIcon from "@mui/icons-material/Search";
import type { Author } from "@/types/author";
import { formatAuthorLabel } from "@/components/StyleText/authorLabel";

function authorMatchesQuery(author: Author, query: string): boolean {
  const q = query.trim().toLowerCase();
  if (!q) return true;
  const label = formatAuthorLabel(author).toLowerCase();
  if (label.includes(q)) return true;
  const parts = [author.name, author.surname, author.last_name]
    .filter(Boolean)
    .map((s) => s.toLowerCase());
  return parts.some((p) => p.includes(q));
}

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

  const filtered = useMemo(
    () => authors.filter((a) => authorMatchesQuery(a, search)),
    [authors, search],
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
          Загрузка авторов…
        </Typography>
      </Paper>
    );
  }

  const selectedInFiltered = filtered.filter((a) => selectedIds.includes(a.id)).length;

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
          Авторы для сравнения
        </Typography>
        <TextField
          size="small"
          fullWidth
          placeholder="Поиск по имени или фамилии…"
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
        <Stack direction="row" spacing={1} sx={{ mt: 1 }} flexWrap="wrap" useFlexGap>
          <Button size="small" onClick={handleClearSelection} disabled={selectedIds.length === 0}>
            Снять выбор
          </Button>
          <Button
            size="small"
            onClick={handleSelectFiltered}
            disabled={filtered.length === 0}
          >
            Выбрать всех в списке
          </Button>
        </Stack>
        <FormHelperText sx={{ mx: 0, mt: 1 }}>
          Не выбран ни один автор — поиск по всем доступным. Иначе только среди
          отмеченных ({selectedIds.length}
          {filtered.length !== authors.length
            ? ` · в списке ${filtered.length} из ${authors.length}`
            : ""}
          ).
        </FormHelperText>
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
              primary="Никого не найдено"
              secondary="Измените запрос поиска"
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

      {filtered.length > 0 && selectedInFiltered > 0 && (
        <Box sx={{ px: 2, py: 1, borderTop: 1, borderColor: "divider" }}>
          <Typography variant="caption" color="text.secondary">
            Отмечено в этом списке: {selectedInFiltered} из {filtered.length}
          </Typography>
        </Box>
      )}
    </Paper>
  );
}
