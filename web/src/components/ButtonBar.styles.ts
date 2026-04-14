import { styled } from "@mui/material";

export const StatusWrapper = styled('div')(({ }) => ({
  padding: 16,
  display: "flex",
  flexDirection: "column",
  placeContent: "center",
  width: "100%",
  div: {
    height: "1.5em"
  },
}));