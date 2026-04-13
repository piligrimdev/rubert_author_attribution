import { createTheme } from "@mui/material/styles";

export const theme = createTheme({
  palette: {
    mode: "light",
    primary: {
      main: "#6D4C41",
      light: "#9C786C",
      dark: "#40241A",
      contrastText: "#FFFBF5",
    },
    secondary: {
      main: "#8D6E63",
      light: "#BE9E91",
      dark: "#5F4339",
    },
    background: {
      default: "#F5F0EB",
      paper: "#FFFBF5",
    },
    text: {
      primary: "#3E2723",
      secondary: "#6D4C41",
    },
    divider: "rgba(109, 76, 65, 0.12)",
    error: { main: "#C62828" },
    warning: { main: "#E65100" },
    success: { main: "#558B2F" },
  },
  typography: {
    fontFamily: "'Inter', 'Roboto', sans-serif",
    h4: {
      fontWeight: 700,
      fontFamily: "'Playfair Display', 'Georgia', serif",
    },
    h5: {
      fontWeight: 600,
      fontFamily: "'Playfair Display', 'Georgia', serif",
    },
    h6: { fontWeight: 600 },
  },
  shape: { borderRadius: 12 },
  components: {
    MuiButton: {
      styleOverrides: {
        root: { textTransform: "none", fontWeight: 600 },
        contained: {
          boxShadow: "none",
          "&:hover": { boxShadow: "0 2px 8px rgba(109,76,65,0.25)" },
        },
      },
    },
    MuiPaper: {
      defaultProps: { elevation: 0 },
      styleOverrides: {
        root: {
          backgroundImage: "none",
          border: "1px solid",
          borderColor: "rgba(109, 76, 65, 0.12)",
        },
      },
    },
    MuiAppBar: {
      styleOverrides: {
        root: {
          backgroundImage: "none",
        },
      },
    },
    MuiChip: {
      styleOverrides: {
        root: { fontWeight: 500 },
      },
    },
    MuiTextField: {
      defaultProps: {
        variant: "outlined",
      },
    },
    MuiOutlinedInput: {
      styleOverrides: {
        root: {
          "&:hover .MuiOutlinedInput-notchedOutline": {
            borderColor: "rgba(109, 76, 65, 0.4)",
          },
        },
      },
    },
    MuiStepIcon: {
      styleOverrides: {
        root: {
          "&.Mui-completed": { color: "#6D4C41" },
          "&.Mui-active": { color: "#6D4C41" },
        },
      },
    },
  },
});
