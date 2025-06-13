import styled from "@emotion/styled";
import { FormControl, FormGroup } from "@mui/material";

export const StyledFormGroup = styled(FormGroup)(({ theme }) => ({
  display: "grid",
  gridTemplateColumns: "repeat(6, 1fr)",
  gap: "10px",
  flexGrow: 1,
  div: {
    display: "flex",
    gap: "10px",
    width: "100%",
    flexDirection: "row"
  }
}));

export const LibraryFormControl = styled(FormControl)(({ theme }) => ({
  gridColumn: "span 2"
}));

export const MediaFormControl = styled(FormControl)(({ theme }) => ({
  gridColumn: "span 2"
}));

export const ContentFormControl = styled(FormControl)(({ theme }) => ({
  gridColumn: "span 2"
}));

export const NameIdFormControl = styled(FormControl)(({ theme }) => ({
  gridColumn: "span 4"
}));

export const SeasonFormControl = styled(FormControl)(({ theme }) => ({
  gridColumn: "span 1"
}));

export const FirstEpisodeFormControl = styled(FormControl)(({ theme }) => ({
  gridColumn: "span 1"
}));