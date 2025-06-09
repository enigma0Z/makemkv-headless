import styled from "@emotion/styled";
import { FormGroup } from "@mui/material";

export const StyledFormGroup = styled(FormGroup)(({ theme }) => ({
  display: "flex",
  flexDirection: "column",
  gap: "10px",
  flexGrow: 1,
  div: {
    display: "flex",
    gap: "10px",
    width: "100%",
    flexDirection: "row"
  }
}));
