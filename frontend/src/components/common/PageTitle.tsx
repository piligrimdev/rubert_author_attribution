import Typography from "@mui/material/Typography";
import type { SxProps, Theme } from "@mui/material/styles";

interface PageTitleProps {
  children: React.ReactNode;
  subtitle?: string;
  sx?: SxProps<Theme>;
}

export default function PageTitle({ children, subtitle, sx }: PageTitleProps) {
  return (
    <>
      <Typography variant="h4" gutterBottom sx={sx}>
        {children}
      </Typography>
      {subtitle && (
        <Typography variant="body1" color="text.secondary" sx={{ mb: 3 }}>
          {subtitle}
        </Typography>
      )}
    </>
  );
}
