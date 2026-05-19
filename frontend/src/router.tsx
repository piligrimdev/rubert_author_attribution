import { createBrowserRouter } from "react-router-dom";
import Layout from "@/components/Layout/Layout";
import ProtectedRoute from "@/components/Auth/ProtectedRoute";
import HomePage from "@/pages/HomePage";
import StyleTextPage from "@/pages/StyleTextPage";
import AuthorsPage from "@/pages/AuthorsPage";
import AuthorDetailPage from "@/pages/AuthorDetailPage";
import AddAuthorPage from "@/pages/AddAuthorPage";
import ImportCorpusPage from "@/pages/ImportCorpusPage";
import LoginPage from "@/pages/LoginPage";
import RegisterPage from "@/pages/RegisterPage";
import NotFoundPage from "@/pages/NotFoundPage";

export const router = createBrowserRouter([
  {
    element: <Layout />,
    children: [
      { path: "login", element: <LoginPage /> },
      { path: "register", element: <RegisterPage /> },
      {
        element: <ProtectedRoute />,
        children: [
          { index: true, element: <HomePage /> },
          { path: "style", element: <StyleTextPage /> },
          { path: "authors", element: <AuthorsPage /> },
          { path: "authors/new", element: <AddAuthorPage /> },
          { path: "authors/import", element: <ImportCorpusPage /> },
          { path: "authors/:id", element: <AuthorDetailPage /> },
        ],
      },
      { path: "*", element: <NotFoundPage /> },
    ],
  },
]);
