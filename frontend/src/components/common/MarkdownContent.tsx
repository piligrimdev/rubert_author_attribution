import type { Components } from "react-markdown";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import Box from "@mui/material/Box";
import Typography from "@mui/material/Typography";
import Link from "@mui/material/Link";
import Divider from "@mui/material/Divider";
import Paper from "@mui/material/Paper";
import Table from "@mui/material/Table";
import TableBody from "@mui/material/TableBody";
import TableCell from "@mui/material/TableCell";
import TableContainer from "@mui/material/TableContainer";
import TableHead from "@mui/material/TableHead";
import TableRow from "@mui/material/TableRow";
import { Link as RouterLink } from "react-router-dom";

interface MarkdownContentProps {
  content: string;
}

const markdownComponents: Components = {
  h1: ({ children }) => (
    <Typography
      variant="h4"
      component="h1"
      gutterBottom
      sx={{ fontFamily: "'Playfair Display', serif", mb: 2 }}
    >
      {children}
    </Typography>
  ),
  h2: ({ children }) => (
    <Typography
      variant="h5"
      component="h2"
      gutterBottom
      sx={{ fontFamily: "'Playfair Display', serif", mt: 3, mb: 1.5 }}
    >
      {children}
    </Typography>
  ),
  h3: ({ children }) => (
    <Typography variant="h6" component="h3" gutterBottom sx={{ mt: 2.5, mb: 1 }}>
      {children}
    </Typography>
  ),
  p: ({ children }) => (
    <Typography variant="body1" component="p" paragraph sx={{ lineHeight: 1.75 }}>
      {children}
    </Typography>
  ),
  strong: ({ children }) => (
    <Box component="strong" sx={{ fontWeight: 700 }}>
      {children}
    </Box>
  ),
  em: ({ children }) => (
    <Box component="em" sx={{ fontStyle: "italic" }}>
      {children}
    </Box>
  ),
  a: ({ href, children }) => {
    if (href?.startsWith("/")) {
      return (
        <Link component={RouterLink} to={href} underline="hover">
          {children}
        </Link>
      );
    }
    return (
      <Link href={href} target="_blank" rel="noopener noreferrer" underline="hover">
        {children}
      </Link>
    );
  },
  ul: ({ children }) => (
    <Box
      component="ul"
      sx={{
        pl: 3,
        mb: 2,
        "& li": { mb: 0.75, lineHeight: 1.7 },
      }}
    >
      {children}
    </Box>
  ),
  ol: ({ children }) => (
    <Box
      component="ol"
      sx={{
        pl: 3,
        mb: 2,
        "& li": { mb: 0.75, lineHeight: 1.7 },
      }}
    >
      {children}
    </Box>
  ),
  li: ({ children }) => <Box component="li">{children}</Box>,
  blockquote: ({ children }) => (
    <Paper
      variant="outlined"
      sx={{
        px: 2.5,
        py: 1.5,
        my: 2,
        bgcolor: "action.hover",
        borderColor: "divider",
        "& p:last-child": { mb: 0 },
      }}
    >
      {children}
    </Paper>
  ),
  hr: () => <Divider sx={{ my: 3 }} />,
  code: ({ className, children }) => {
    const isBlock = className?.includes("language-");
    if (isBlock) {
      return (
        <Box
          component="pre"
          sx={{
            bgcolor: "action.hover",
            borderRadius: 1,
            px: 2,
            py: 1.5,
            my: 2,
            overflow: "auto",
            fontFamily: "monospace",
            fontSize: "0.875rem",
            lineHeight: 1.6,
          }}
        >
          <code>{children}</code>
        </Box>
      );
    }
    return (
      <Box
        component="code"
        sx={{
          bgcolor: "action.hover",
          borderRadius: 0.5,
          px: 0.75,
          py: 0.25,
          fontFamily: "monospace",
          fontSize: "0.875em",
        }}
      >
        {children}
      </Box>
    );
  },
  table: ({ children }) => (
    <TableContainer component={Paper} variant="outlined" sx={{ my: 2 }}>
      <Table size="small">{children}</Table>
    </TableContainer>
  ),
  thead: ({ children }) => <TableHead>{children}</TableHead>,
  tbody: ({ children }) => <TableBody>{children}</TableBody>,
  tr: ({ children }) => <TableRow>{children}</TableRow>,
  th: ({ children }) => (
    <TableCell sx={{ fontWeight: 700, bgcolor: "action.hover" }}>{children}</TableCell>
  ),
  td: ({ children }) => <TableCell>{children}</TableCell>,
};

export default function MarkdownContent({ content }: MarkdownContentProps) {
  return (
    <Box sx={{ maxWidth: 800 }}>
      <ReactMarkdown remarkPlugins={[remarkGfm]} components={markdownComponents}>
        {content}
      </ReactMarkdown>
    </Box>
  );
}
