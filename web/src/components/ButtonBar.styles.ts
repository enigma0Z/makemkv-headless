import styled from "@emotion/styled";

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