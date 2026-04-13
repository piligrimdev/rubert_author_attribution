import Grid from "@mui/material/Grid2";
import type { Author } from "@/types/author";
import AuthorCard from "./AuthorCard";

interface AuthorsGridProps {
  authors: Author[];
}

export default function AuthorsGrid({ authors }: AuthorsGridProps) {
  return (
    <Grid container spacing={2}>
      {authors.map((author) => (
        <Grid key={author.id} size={{ xs: 12, sm: 6, md: 4 }}>
          <AuthorCard author={author} />
        </Grid>
      ))}
    </Grid>
  );
}
