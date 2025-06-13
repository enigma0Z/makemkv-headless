import { Card, IconButton, LinearProgress } from "@mui/material";
import { useContext, useEffect, useState } from "react"
import { StatusScrollerWrapper, StatusScrollerWrapperMinimized } from "./StatusScroller.styles";

import ExpandLessIcon from '@mui/icons-material/ExpandLess';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import { Context as SocketContext } from "../socket/Context";

export const StatusScroller = () => {
  const { connected, messageEvents } = useContext(SocketContext)

  const [isMinimized, setIsMinimized] = useState<boolean>(false)

  const messages = messageEvents?.map((event) => event.text)

  const handleOnScroll = () => { };

  useEffect(() => {
    const scroller = document.getElementById('status-scroller')
    scroller?.scrollTo({top: scroller.scrollHeight})
  }, [messages])
  
  const WrapperComponent = isMinimized 
    ? StatusScrollerWrapperMinimized
    : StatusScrollerWrapper

  return <Card sx={{ position: "relative" }}>
    <IconButton 
      disableRipple
      sx={{ 
        display: "flex",
        position: "absolute",
        top: "0",
        right: "0"
      }} 
      onClick={() => {
        setIsMinimized((prev) => !prev)
      }}
    >
      { isMinimized 
        ? <ExpandMoreIcon />
        : <ExpandLessIcon />
      }
    </IconButton>
    <WrapperComponent id="status-scroller" >
      {messages?.map(message => (
        <div>{message}</div>
      ))}
    </WrapperComponent>
    { connected
      ? <LinearProgress variant="determinate" value={0} /> 
      : <LinearProgress variant="determinate" color="error" value={0} />
    }
  </Card>
}