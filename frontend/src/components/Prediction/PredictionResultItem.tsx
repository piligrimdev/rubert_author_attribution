import Box from "@mui/material/Box";
import Typography from "@mui/material/Typography";
import Chip from "@mui/material/Chip";
import Stack from "@mui/material/Stack";
import type { NearestTextItem } from "@/types/prediction";

interface Props {
  item: NearestTextItem;
  rank: number;
}

export default function PredictionResultItem({ item, rank }: Props) {
  const isTop = rank === 1;
  const truncatedText =
    item.text.length > 300 ? item.text.slice(0, 300) + "…" : item.text;

  return (
    <Box sx={{ py: 2 }}>
      <Stack direction="row" alignItems="center" spacing={1} sx={{ mb: 1 }}>
        <Typography
          variant="subtitle2"
          sx={{
            bgcolor: "primary.main",
            color: "primary.contrastText",
            width: 28,
            height: 28,
            borderRadius: "50%",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            fontSize: 13,
            flexShrink: 0,
          }}
        >
          {rank}
        </Typography>
        <Typography variant="subtitle1" fontWeight={isTop ? 700 : 500}>
          {item.author}
        </Typography>
        {isTop && (
          <Chip label="Ближайший" color="primary" size="small" />
        )}
        <Box sx={{ flexGrow: 1 }} />
        <Chip
          label={`Расстояние: ${item.distance.toFixed(4)}`}
          size="small"
          variant="outlined"
          color={isTop ? "primary" : "default"}
        />
      </Stack>
      <Typography
        variant="body2"
        color="text.secondary"
        sx={{
          pl: 5,
          fontStyle: "italic",
          whiteSpace: "pre-line",
          lineHeight: 1.6,
        }}
      >
        «{truncatedText}»
      </Typography>
    </Box>
  );
}
