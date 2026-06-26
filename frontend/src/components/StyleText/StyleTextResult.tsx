import Paper from "@mui/material/Paper";
import Typography from "@mui/material/Typography";
import Fade from "@mui/material/Fade";
import { strings } from "@/i18n/strings";

interface StyleTextResultProps {
  text: string;
}

export default function StyleTextResult({ text }: StyleTextResultProps) {
  return (
    <Fade in>
      <Paper sx={{ p: 3, mt: 3 }}>
        <Typography variant="h6" gutterBottom>
          {strings.styleText.resultTitle}
        </Typography>
        <Typography
          component="div"
          sx={{
            whiteSpace: "pre-wrap",
            wordBreak: "break-word",
            lineHeight: 1.65,
          }}
        >
          {text}
        </Typography>
      </Paper>
    </Fade>
  );
}
