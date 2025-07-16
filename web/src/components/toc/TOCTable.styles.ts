import styled from "@emotion/styled";
import { Box, RadioGroup, TableCell, TableRow } from "@mui/material";

export const StyledTableCellTop = styled(TableCell)(({ theme }) => ({
  borderBottom: "None",
  [ theme.breakpoints.down('md') ]: {
    paddingBottom: 0
  }
}));

export const StyledTableCellMiddle = styled(TableCell)(({ theme }) => ({
  borderTop: "None",
  padding: 0,
  ".MuiCollapse-wrapperInner": {
    paddingBottom: 16,
    paddingLeft: 16,
    paddingRight: 16,
    display: "flex",
    flexDirection: "column",
    "> .MuiBox-root:first-of-type": {
      span: {
        paddingRight: 8,
        paddingLeft: 8,
        borderRight: "solid .5px grey",
        color: "grey"
      },
      "> span:first-of-type": {
        paddingLeft: 0,
      },
      "> span:last-of-type": {
        paddingRight: 0,
        borderRight: "none"
      }
    },
    ".MuiBox-root": {
      paddingLeft: 16,
      paddingRight: 16,
    },
    // "> div:nth-of-type(1)": {
    //   paddingLeft: 16,
    //   paddingRight: 16
    // }
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

export const ProgressCellHeader = styled(TableCell)(({ theme }) => ({
  [ theme.breakpoints.down('md') ]: {
    display: "none"
  }
}));

export const ProgressCell = styled(StyledTableCellTop)(({ theme }) => ({
  [ theme.breakpoints.down('md') ]: {
    display: "none"
  }
}));