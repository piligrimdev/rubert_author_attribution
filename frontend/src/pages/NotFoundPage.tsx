import Stack from "@mui/material/Stack";
import Typography from "@mui/material/Typography";
import Button from "@mui/material/Button";
import { Link } from "react-router-dom";
import { strings } from "@/i18n/strings";

export default function NotFoundPage() {
  return (
    <Stack
      alignItems="center"
      justifyContent="center"
      sx={{ py: 10 }}
      spacing={2}
    >
      <Typography variant="h1" fontWeight={800} color="text.secondary">
        404
      </Typography>
      <Typography variant="h5" color="text.secondary">
        {strings.notFound.title}
      </Typography>
      <Button component={Link} to="/" variant="contained" sx={{ mt: 2 }}>
        {strings.notFound.backHome}
      </Button>
    </Stack>
  );
}
