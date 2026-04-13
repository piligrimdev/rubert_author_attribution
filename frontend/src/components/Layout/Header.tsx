import AppBar from "@mui/material/AppBar";
import Toolbar from "@mui/material/Toolbar";
import Typography from "@mui/material/Typography";
import Container from "@mui/material/Container";
import Button from "@mui/material/Button";
import Box from "@mui/material/Box";
import AutoStoriesIcon from "@mui/icons-material/AutoStories";
import LogoutIcon from "@mui/icons-material/Logout";
import { Link, useLocation } from "react-router-dom";
import { useAuth } from "@/context/AuthContext";

const NAV_ITEMS = [
  { label: "Атрибуция", to: "/" },
  { label: "Стилизация", to: "/style" },
  { label: "Авторы", to: "/authors" },
] as const;

export default function Header() {
  const { pathname } = useLocation();
  const { isAuthenticated, logout } = useAuth();

  return (
    <AppBar
      position="sticky"
      elevation={0}
      sx={{
        bgcolor: "background.paper",
        borderBottom: 1,
        borderColor: "divider",
      }}
    >
      <Container maxWidth="lg">
        <Toolbar disableGutters sx={{ gap: 1.5 }}>
          <AutoStoriesIcon sx={{ color: "primary.main" }} />
          <Typography
            variant="h6"
            component={Link}
            to="/"
            sx={{
              textDecoration: "none",
              color: "text.primary",
              mr: 2,
              fontFamily: "'Playfair Display', serif",
            }}
          >
            Атрибуция текста
          </Typography>

          {isAuthenticated &&
            NAV_ITEMS.map((item) => {
              const active =
                item.to === "/"
                  ? pathname === "/"
                  : pathname.startsWith(item.to);
              return (
                <Button
                  key={item.to}
                  component={Link}
                  to={item.to}
                  color={active ? "primary" : "inherit"}
                  sx={{
                    fontWeight: active ? 700 : 400,
                    color: active ? "primary.main" : "text.secondary",
                  }}
                >
                  {item.label}
                </Button>
              );
            })}

          <Box sx={{ flexGrow: 1 }} />

          {isAuthenticated && (
            <Button
              onClick={logout}
              color="inherit"
              startIcon={<LogoutIcon />}
              sx={{ color: "text.secondary" }}
            >
              Выйти
            </Button>
          )}
        </Toolbar>
      </Container>
    </AppBar>
  );
}
