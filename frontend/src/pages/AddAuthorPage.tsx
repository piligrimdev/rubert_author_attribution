import { useState } from "react";
import { useNavigate } from "react-router-dom";
import Stack from "@mui/material/Stack";
import Alert from "@mui/material/Alert";
import Stepper from "@mui/material/Stepper";
import Step from "@mui/material/Step";
import StepLabel from "@mui/material/StepLabel";
import Button from "@mui/material/Button";
import PageTitle from "@/components/common/PageTitle";
import AddAuthorForm from "@/components/Authors/AddAuthorForm";
import AddTextForm from "@/components/Authors/AddTextForm";
import { useCreateAuthor } from "@/hooks/useAuthors";
import { useAddText } from "@/hooks/useTexts";
import type { CreateAuthorRequest, Author } from "@/types/author";

const STEPS = ["Данные автора", "Добавление текста"];

export default function AddAuthorPage() {
  const navigate = useNavigate();
  const createAuthorMutation = useCreateAuthor();
  const addTextMutation = useAddText();

  const [activeStep, setActiveStep] = useState(0);
  const [createdAuthor, setCreatedAuthor] = useState<Author | null>(null);

  const handleCreateAuthor = (data: CreateAuthorRequest) => {
    createAuthorMutation.mutate(data, {
      onSuccess: (author) => {
        setCreatedAuthor(author);
        setActiveStep(1);
      },
    });
  };

  const handleAddText = (data: { text: string; genre_name: string }) => {
    if (!createdAuthor) return;
    addTextMutation.mutate(
      {
        text: data.text,
        author_id: createdAuthor.id,
        genre_name: data.genre_name,
      },
      {
        onSuccess: () => {
          navigate(`/authors/${createdAuthor.id}`);
        },
      },
    );
  };

  const fullName = createdAuthor
    ? [createdAuthor.surname, createdAuthor.name, createdAuthor.last_name]
        .filter(Boolean)
        .join(" ")
    : "";

  return (
    <Stack spacing={3}>
      <PageTitle subtitle="Создайте автора и добавьте его текст в базу данных">
        Новый автор
      </PageTitle>

      <Stepper activeStep={activeStep} sx={{ mb: 1 }}>
        {STEPS.map((label) => (
          <Step key={label}>
            <StepLabel>{label}</StepLabel>
          </Step>
        ))}
      </Stepper>

      {createAuthorMutation.error && (
        <Alert severity="error">
          Не удалось создать автора: {createAuthorMutation.error.message}
        </Alert>
      )}
      {addTextMutation.error && (
        <Alert severity="error">
          Не удалось добавить текст: {addTextMutation.error.message}
        </Alert>
      )}

      {activeStep === 0 && (
        <AddAuthorForm
          onSubmit={handleCreateAuthor}
          isLoading={createAuthorMutation.isPending}
        />
      )}

      {activeStep === 1 && (
        <>
          <Alert severity="success">
            Автор <strong>{fullName}</strong> успешно создан! Теперь добавьте
            текст.
          </Alert>
          <AddTextForm
            onSubmit={handleAddText}
            isLoading={addTextMutation.isPending}
          />
          <Button
            variant="text"
            onClick={() => navigate(`/authors/${createdAuthor!.id}`)}
            sx={{ alignSelf: "flex-start" }}
          >
            Пропустить и перейти к автору
          </Button>
        </>
      )}
    </Stack>
  );
}
