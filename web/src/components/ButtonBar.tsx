import { AppBar, Button, IconButton, Toolbar, Tooltip } from "@mui/material";
import { useAppDispatch, useAppSelector } from "@/api/store";
import { socketActions } from "@/api/store/socket";
import endpoints from "@/api/endpoints";
import { tocActions } from "@/api/store/toc";
import { ConfirmationDialog } from "./ConfirmationModal";
import { useState } from "react";

import MenuIcon from '@mui/icons-material/Menu';
import EjectIcon from '@mui/icons-material/Eject';
import SaveAltIcon from '@mui/icons-material/SaveAlt';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import CancelIcon from '@mui/icons-material/Cancel';

type Props = {}

export const ButtonBar = ({ }: Props) => {
  const dispatch = useAppDispatch()

  const sortInfo = useAppSelector((state) => state.rip.sort_info)
  const library = useAppSelector((state) => state.rip.destination?.library)
  const media = useAppSelector((state) => state.rip.destination?.media)
  const content = useAppSelector((state) => state.rip.destination?.content)
  const ripAll = useAppSelector((state) => state.rip.rip_all)

  const ripState = useAppSelector((state) => state.socket.ripState)

  const [cancelModalOpen, setCancelModalOpen] = useState<boolean>(false)

  const handleEject = () => {
    console.info('Ejecting disc')
    dispatch(socketActions.resetSocketState({}))
    fetch(endpoints.eject(), { method: 'GET' })
  }

  const handleLoadToc = () => {
    console.info('Fetching TOC')
    dispatch(tocActions.setTocData(undefined))
    // fetch(endpoints.state.resetSocket(), { method: 'GET' })
    fetch(endpoints.toc(), { method: 'GET' })
      .then(response => response.json())
      .then(json => {
        dispatch(tocActions.setTocData(json))
      })
  }

  const handleCancelRip = () => {
    fetch(endpoints.rip.stop(), {
      method: 'GET'
    }).then((response) => {
      console.log('Rip stop response', response)
    })
  };

  const handleStartRip = () => {
    if (ripState?.rip_started) {
      setCancelModalOpen(true)
    } else {
      dispatch(socketActions.resetSocketState({ rip_started: true }))
      fetch(endpoints.rip.start(), {
        method: 'POST',
        body: JSON.stringify({
          rip_all: ripAll,
          destination: `${library}/${content}s/${media}`,
          sort_info: sortInfo
        }),
        headers: new Headers({
          "Content-Type": "application/json"
        })
      })
    }
  }

  return <>
    <AppBar>
      <Toolbar>
        <Tooltip title="Menu">
          <IconButton>
            <MenuIcon />
          </IconButton>
        </Tooltip>
        <Tooltip title="Eject Disc">
          <IconButton
            onClick={handleEject}
            disabled={ripState?.rip_started}
          >
            <EjectIcon />
          </IconButton>
        </Tooltip>
        <Tooltip title="Load ToC (Table of Contents)">
          <IconButton
            onClick={handleLoadToc}
            disabled={ripState?.rip_started}
          >
            <SaveAltIcon />
          </IconButton>
        </Tooltip>
        <Button
          sx={{ marginLeft: "auto" }}
          onClick={handleStartRip}
          variant="outlined"
          startIcon={ ripState?.rip_started ? <CancelIcon /> : <CheckCircleIcon /> }
        >
          { ripState?.rip_started 
            ? "Cancel Rip"
            : "Start Rip"
          }
        </Button>
        <ConfirmationDialog
          open={cancelModalOpen}
          onClose={() => { setCancelModalOpen(false) }}
          onConfirm={() => { handleCancelRip() }}
          title={'Cancel Rip?'}
          message={'This disc will not get uploaded if it is cancelled now'}
        />
      </Toolbar>
    </AppBar>
    <div style={{ height: "4rem" }} />
  </>
}