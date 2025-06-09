import styled from "@emotion/styled";
import { RadioGroup, TableCell } from "@mui/material";

export const WidgetCell = styled(TableCell)(({ theme }) => ({
  size: 0
}));

export const StatusCell = styled(TableCell)(({ theme }) => ({}));

export const WidgetWrapper = styled.div(({ theme }) => ({
  display: "flex",
  flexDirection: "row",
  flexWrap: "nowrap"
}));

export const StatusWrapper = styled.div(({ theme }) => ({
  display: "flex",
  flexDirection: "column",
  placeContent: "center",
  width: "100%",
  div: {
    height: "1.5em"
  }
}));

export const MainExtrasRadioGroup = styled(RadioGroup)(({ theme }) => ({
  display: "flex",
  flexDirection: "row",
  flexWrap: "nowrap"
}));