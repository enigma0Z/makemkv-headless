import styled from "@emotion/styled";
import { RadioGroup, TableCell } from "@mui/material";

export const WidgetCell = styled(TableCell)(({ }) => ({
  size: 0
}));

export const StatusContentWrapper = styled.div(({ }) => ({
  display: "flex",
  flexDirection: "row",
  justifyContent: "space-around"
}));

export const StatusContentWrapperLeft = styled.div(({ }) => ({
  width: "30%"
}));

export const WidgetWrapper = styled.div(({ }) => ({
  display: "flex",
  flexDirection: "row",
  flexWrap: "nowrap"
}));

export const StatusWrapper = styled.div(({ }) => ({
  display: "flex",
  flexDirection: "column",
  placeContent: "center",
  width: "70%",
  div: {
    height: "1.5em"
  }
}));

export const MainExtrasRadioGroup = styled(RadioGroup)(({ }) => ({
  display: "flex",
  flexDirection: "row",
  flexWrap: "nowrap"
}));