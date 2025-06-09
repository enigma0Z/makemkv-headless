import styled from "@emotion/styled";

export const StatusScrollerWrapper = styled.div(({ theme }) => ({
  lineHeight: "1.5em",
  height: "27em",
  overflowY: "scroll",
  scrollSnapAlign: "end",
  padding: "10px",
  fontFamily: "monospace"
}));