import { Card, IconButton, LinearProgress } from "@mui/material";
import { useEffect, useState } from "react"
import { StatusScrollerWrapper, StatusScrollerWrapperMinimized } from "./StatusScroller.styles";

import ExpandLessIcon from '@mui/icons-material/ExpandLess';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import { useAppSelector } from "@/api";

export type Props = {
  minimized?: boolean
  showMinimizeButton?: boolean
  id?: string
}

export const StatusScroller = ({ minimized = false, showMinimizeButton = true, id = "default" }: Props) => {

  const connected = useAppSelector((state) => state.socket.ripState.connected )
  const messages = useAppSelector((state) => state.socket.messages)

  const [isMinimized, setIsMinimized] = useState<boolean>(minimized)

  const handleOnScroll = () => { };

  useEffect(() => {
    const scroller = document.getElementById(`status-scroller-${id}`)
    console.debug('Scroll to bottom')
    scroller?.scrollTo({top: scroller.scrollHeight})
  }, [messages])
  
  const WrapperComponent = isMinimized 
    ? StatusScrollerWrapperMinimized
    : StatusScrollerWrapper

  return <Card sx={{ position: "relative" }}>
    { showMinimizeButton && <IconButton 
      disableRipple
      sx={{ 
        display: "flex",
        position: "absolute",
        top: "0",
        left: "0"
      }} 
      onClick={() => {
        setIsMinimized((prev) => !prev)
      }}
    >
      { isMinimized 
        ? <ExpandMoreIcon />
        : <ExpandLessIcon />
      }
    </IconButton> }
    <WrapperComponent id={`status-scroller-${id}`} >
      {messages?.map((message, index) => (
        <div key={index}>{message}</div>
      ))}
    </WrapperComponent>
    { connected
      ? <LinearProgress variant="determinate" value={0} /> 
      : <LinearProgress variant="determinate" color="error" value={0} />
    }
  </Card>
}