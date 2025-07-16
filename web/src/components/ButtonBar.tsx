import { Button } from "@mui/material";
import { useContext } from "react";
import { Context } from "./socket/Context";

type Props = {
  onEject: () => void;
  onLoadToc: () => void;
  onStartRip: () => void;
  ripDisabled: boolean;
}

export const ButtonBar = ({ onEject, onLoadToc, onStartRip, ripDisabled }: Props) => {
  const { ripState } = useContext(Context)

  return <div>
    <Button
      onClick={ onEject }
      disabled={ ripState?.rip_started }
    >
      Eject
    </Button>
    <Button
      onClick={ onLoadToc }
      disabled={ ripState?.rip_started }
    >
      Load TOC
    </Button>
    <Button
      onClick={ onStartRip }
    >
      { ripState?.rip_started ? "Cancel Rip" : "Start Rip" }
    </Button>
  </div>
}