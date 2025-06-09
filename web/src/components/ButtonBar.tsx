import { Button } from "@mui/material";

type Props = {
  onLoadToc: () => void;
  onStartRip: () => void;
}

export const ButtonBar = ({ onLoadToc, onStartRip }: Props) => {
  return <div>
    <Button
      onClick={onLoadToc}
    >
      Load TOC
    </Button>
    <Button
      onClick={onStartRip}
    >
      Start Rip
    </Button>
  </div>
}