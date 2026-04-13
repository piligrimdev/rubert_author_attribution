import Card from "@mui/material/Card";
import CardContent from "@mui/material/CardContent";
import CardActionArea from "@mui/material/CardActionArea";
import Typography from "@mui/material/Typography";
import Chip from "@mui/material/Chip";
import Stack from "@mui/material/Stack";
import AdminPanelSettingsIcon from "@mui/icons-material/AdminPanelSettings";
import { Link } from "react-router-dom";
import type { Author } from "@/types/author";

interface AuthorCardProps {
  author: Author;
}

function formatFullName(a: Author): string {
  return [a.surname, a.name, a.last_name].filter(Boolean).join(" ");
}

export default function AuthorCard({ author }: AuthorCardProps) {
  const isAdmin = author.provided_by === null;

  return (
    <Card sx={{ height: "100%" }}>
      <CardActionArea component={Link} to={`/authors/${author.id}`} sx={{ height: "100%" }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            {formatFullName(author)}
          </Typography>
          <Stack direction="row" spacing={1} alignItems="center" flexWrap="wrap">
            {isAdmin && (
              <Chip
                icon={<AdminPanelSettingsIcon />}
                label="Добавлен администратором"
                size="small"
                color="default"
                variant="outlined"
              />
            )}
          </Stack>
        </CardContent>
      </CardActionArea>
    </Card>
  );
}
