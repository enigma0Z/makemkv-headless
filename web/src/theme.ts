import styled from "@emotion/styled"
import { Autocomplete as MUIAutocomplete } from "@mui/material";
import { createTheme } from "@mui/material/styles";

export const theme = createTheme({
  palette: {
    mode: "dark",
    background: {
      default: "black"
    }
  }
})

export const AutocompleteWrapper = styled.div(({ theme }) => ({
  ".MuiAutocomplete-endAdornment": { // Fix for weird spacing on buttons
    justifyContent: "right"
  }
}));