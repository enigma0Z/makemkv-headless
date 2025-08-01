import styled from "@emotion/styled";
import { Collapse, IconButton, RadioGroup } from "@mui/material";

const GridWidth = 24

export const TOCGridContainer = styled.div(({ theme }) => ({
  display: "grid",
  gridTemplateColumns: `repeat(${GridWidth}, 1fr)`,
  "> div": {
    display: "flex",
    flexDirection: "row",
    alignItems: "center"
  }
}));

export const CheckboxCell = styled.div(({ theme }) => ({
  gridColumn: "span 1",
}))

export const MainExtraCell = styled.div(({ theme }) => ({
  gridColumn: "span 3",
  [theme.breakpoints.down("md")]: {
    gridColumn: `span ${5}`
  },
  [theme.breakpoints.down("sm")]: {
    gridColumn: `span ${9}`
  },
}))

export const EpisodeCell = styled.div(({ theme }) => ({
  gridColumn: "span 3",
  "> .MuiIconButton-root": {
    padding: 0
  },
  "> .MuiIconButton-root:first-of-type": {
    marginLeft: 10
  },
  [theme.breakpoints.down("md")]: {
    gridColumn: `span ${5}`,
    alignItems: "flex-start"
  },
  [theme.breakpoints.down("sm")]: {
    gridColumn: `span ${9}`,
    "> .MuiIconButton-root": {
      padding: 4,
    },
  },
}))

export const RuntimeCell = styled.div(({ theme }) => ({
  gridColumn: "span 3",
  [theme.breakpoints.down("md")]: {
    gridColumn: `span ${3}`
  },
  [theme.breakpoints.down("sm")]: {
    gridColumn: `13 / span ${6}`,
    // paddingLeft: 16 
  },
}))

export const FilenameCell = styled.div(({ theme }) => ({
  gridColumn: "span 12",
  [theme.breakpoints.down("md")]: {
    gridColumn: `span ${8}`,
  },
  [theme.breakpoints.down("sm")]: {
    gridColumn: `span ${24}`,
    paddingLeft: 16 
  },
}))

export const FilenameContent = styled.div(({ theme }) => ({
  display: "flex",
  flexDirection: "column",
  alignItems: "flex-start",
  [theme.breakpoints.down("sm")]: {
    width: "100%",
  },
}));

export const FilenameHead = styled.div(({ theme }) => ({
  [theme.breakpoints.down("sm")]: {
    display: "none"
  }
}));

export const BorderCell = styled.div(({ theme }) => ({
  gridColumn: `span ${GridWidth}`,
  margin: 0,
  marginTop: 8,
  padding: 0,
}))

export const DividerCell = styled(BorderCell)(({ theme }) => ({
  borderTop: ".5px solid grey",
  marginBottom: 8,
}));

export const CollapseRow = styled(Collapse)(({ theme }) => ({
  gridColumn: `span ${GridWidth}`,
  div: {
    // alignItems: "normal"
  }
}));

export const FullWidthRow = styled.div(({ theme }) => ({
  gridColumn: `span ${GridWidth}`,
}));

export const DetailsWrapper = styled.div(({ theme }) => ({
  display: "flex",
  flexDirection: "column",
  div: {
    alignItems: "normal"
  },
  "> .MuiBox-root:first-of-type": {
    "> span": {
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
}));

export const StatusWrapper = styled.div(({ theme }) => ({
  padding: 16,
  display: "flex",
  flexDirection: "column",
  placeContent: "center",
  width: "100%",
  div: {
    height: "1.5em"
  },
}));

export const StatusWrapperCell = styled(StatusWrapper)(({ theme }) => ({
  paddingTop: 0
}));

export const MainExtrasRadioGroup = styled(RadioGroup)(({ }) => ({
  display: "flex",
  flexDirection: "row",
  flexWrap: "nowrap"
}));
