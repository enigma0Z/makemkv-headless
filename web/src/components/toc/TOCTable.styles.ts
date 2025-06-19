import styled from "@emotion/styled";
import { RadioGroup, TableCell, TableRow } from "@mui/material";

export const StyledTableCellTop = styled(TableCell)(({ theme }) => ({
  [ theme.breakpoints.down('md') ]: {
    borderBottom: "None",
    paddingBottom: 0
  }
}));

export const StyledTableCellBottom = styled(TableCell)(({ theme }) => ({
  [ theme.breakpoints.down('md') ]: {
    borderTop: "None",
    paddingTop: 0
  }
}));

export const StatusContentWrapper = styled.div(({ theme }) => ({
  display: "flex",
  flexDirection: "row",
  justifyContent: "space-around",
  [theme.breakpoints.down('md')]: {
    flexDirection: "column"
  }
}));

export const StatusContentWrapperLeft = styled.div(({ theme }) => ({
  width: "30%",
  [theme.breakpoints.down('md')]: {
    width: "100%"
  }
}));

export const StatusWrapper = styled.div(({ theme }) => ({
  display: "flex",
  flexDirection: "column",
  placeContent: "center",
  width: "70%",
  div: {
    height: "1.5em"
  },
  [theme.breakpoints.down('md')]: {
    width: "100%"
  }
}));

export const MainExtrasRadioGroup = styled(RadioGroup)(({ }) => ({
  display: "flex",
  flexDirection: "row",
  flexWrap: "nowrap"
}));

export const MobileOnlyTableRow = styled(TableRow)(({ theme }) => ({
  display: "none",
  [ theme.breakpoints.down('md') ]: {
    display: "table-row"
  }
}));

export const ProgressCell = styled(StyledTableCellTop)(({ theme }) => ({
  [ theme.breakpoints.down('md') ]: {
    display: "none"
  }
}));