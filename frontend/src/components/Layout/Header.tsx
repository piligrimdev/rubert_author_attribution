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
import { strings } from "@/i18n/strings";

const AUTH_NAV_ITEMS = [
  { label: strings.header.navAttribution, to: "/" },
  { label: strings.header.navAuthors, to: "/authors" },
  { label: strings.header.navGenres, to: "/genres" },
] as const;

const ABOUT_NAV_ITEM = { label: strings.header.navAbout, to: "/about" } as const;

function isNavActive(pathname: string, to: string): boolean {
  if (to === "/") return pathname === "/";
  return pathname === to || pathname.startsWith(`${to}/`);
}

export default function Header() {
  const { pathname } = useLocation();
  const { isAuthenticated, logout } = useAuth();

  const handleLogout = () => {
    logout().catch(() => undefined);
  };

  const navItems = isAuthenticated
    ? [...AUTH_NAV_ITEMS, ABOUT_NAV_ITEM]
    : [ABOUT_NAV_ITEM];

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
            {strings.app.title}
          </Typography>

          {navItems.map((item) => {
            const active = isNavActive(pathname, item.to);
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
              onClick={handleLogout}
              color="inherit"
              startIcon={<LogoutIcon />}
              sx={{ color: "text.secondary" }}
            >
              {strings.header.logout}
            </Button>
          )}
        </Toolbar>
      </Container>
    </AppBar>
  );
}
