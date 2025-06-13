import { Button } from "@mui/material";

type Props = {
  onLoadToc: () => void;
  onStartRip: () => void;
  ripDisabled: boolean;
}

export const ButtonBar = ({ onLoadToc, onStartRip, ripDisabled }: Props) => {
  return <div>
    <Button
      onClick={onLoadToc}
    >
      Load TOC
    </Button>
    <Button
      onClick={onStartRip}
      disabled={ripDisabled}
    >
      Start Rip
    </Button>
  </div>
}