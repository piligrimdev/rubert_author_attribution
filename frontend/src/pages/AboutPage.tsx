import Paper from "@mui/material/Paper";
import MarkdownContent from "@/components/common/MarkdownContent";
import aboutMarkdown from "@/content/about.md?raw";

export default function AboutPage() {
  return (
    <Paper sx={{ p: { xs: 2.5, md: 4 } }}>
      <MarkdownContent content={aboutMarkdown} />
    </Paper>
  );
}
