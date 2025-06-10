import styled from "@emotion/styled";

export const StatusScrollerWrapper = styled.div(({ theme }) => ({
  lineHeight: "1.5em",
  height: "calc(27em + 20px)",
  overflowY: "scroll",
  scrollSnapAlign: "end",
  padding: "10px",
  fontFamily: "monospace"
}));

export const StatusScrollerWrapperMinimized = styled.div(({ theme }) => ({
  lineHeight: "1.5em",
  height: "calc(4.5em + 20px)",
  overflowY: "scroll",
  scrollSnapAlign: "end",
  padding: "10px",
  fontFamily: "monospace"
}));