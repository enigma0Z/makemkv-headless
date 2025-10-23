import { AppBar, Button, IconButton, LinearProgress, Toolbar, Tooltip, Typography } from "@mui/material";
import { useAppDispatch, useAppSelector } from "@/api";
import { socketActions, type SocketProgress } from "@/api/v1/socket/store";
import { tocActions } from "@/api/v1/toc/store";
import { ConfirmationDialog } from "./ConfirmationModal";
import { useState } from "react";

import MenuIcon from '@mui/icons-material/Menu';
import EjectIcon from '@mui/icons-material/Eject';
import SaveAltIcon from '@mui/icons-material/SaveAlt';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import CancelIcon from '@mui/icons-material/Cancel';
import { StatusWrapper } from "./ButtonBar.styles";
import { endpoints, type ApiModel } from "@/api/endpoints";
import { ripActions, ripSelectors } from "@/api/v1/rip/store";

type Props = {}

export const ButtonBar = ({ }: Props) => {
  const dispatch = useAppDispatch()

  const sortInfo = useAppSelector((state) => state.rip.sort_info)
  const library = useAppSelector((state) => state.rip.destination?.library)
  const media = useAppSelector((state) => state.rip.destination?.media)
  const content = useAppSelector((state) => state.rip.destination?.content)
  const ripState = useAppSelector((state) => state.socket.ripState)
  const ripAll = useAppSelector((state) => ripSelectors.rip_all(state))

  const tocLoading = useAppSelector((state) => state.toc.loading)

  const [cancelModalOpen, setCancelModalOpen] = useState<boolean>(false)

  let current_progress: SocketProgress | undefined
  if (ripState.current_title !== null && ripState.current_title !== undefined) {
    current_progress = ripState.current_progress?.[ripState.current_title]
  }

  const handleEject = () => {
    console.info('Ejecting disc')
    dispatch(socketActions.setSocketState())
    fetch(endpoints.disc.eject(), { method: 'GET' })
  }

  const handleLoadToc = () => {
    console.info('Fetching Toc')
    dispatch(tocActions.setTocLoading(true))
    dispatch(tocActions.setTocData(undefined))
	dispatch(socketActions.setSocketState())
	dispatch(ripActions.setMainIndexes([]))
	dispatch(ripActions.setExtraIndexes([]))
    fetch(endpoints.toc_async(), { method: 'GET' })
  }

  const handleCancelRip = () => {
    fetch(endpoints.rip.stop(), { method: 'GET' })
    .then((response) => response.json() as Promise<ApiModel['v1']['rip.stop']>)
    .then(({ status }) => {
      if (status === 'stopped') {
        dispatch(socketActions.updateSocketState({ rip_started: false }))
      }
    })
  };

  const handleStartRip = () => {
    if (ripState?.rip_started) {
      setCancelModalOpen(true)
    } else {
      dispatch(socketActions.setSocketState({ rip_started: true }))
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
            loading={tocLoading}
          >
            <SaveAltIcon />
          </IconButton>
        </Tooltip>
        <Button
          sx={{ marginLeft: "auto", textWrap: "nowrap", minWidth: 'max-content' }}
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
      { ripState?.total_status && <StatusWrapper>
        <Typography variant="caption">
          {ripState?.total_status
            ? <>{ripState.total_status} ({Math.round((ripState.total_progress?.progress ?? 0) * 10000) / 100}%) </>
            : "Status"
          } {ripState?.current_status && current_progress && <>
            / {ripState.current_status} ({Math.round((current_progress.progress ?? 0) * 10000) / 100}%)
          </>
          }
        </Typography>
        <LinearProgress
          variant="buffer"
          value={ripState?.total_progress?.progress ? ripState.total_progress.progress * 100 : 0}
          valueBuffer={ripState?.total_progress?.buffer ? ripState.total_progress.buffer * 100 : 0}
        />
        {ripState?.current_status && current_progress && <>
          <LinearProgress
            variant="buffer"
            valueBuffer={(current_progress.buffer ?? 1) * 100}
            value={(current_progress.progress ?? 0) * 100}
          />
        </>}
      </StatusWrapper> }
    </AppBar>
    <div style={{ height: ripState?.total_status ? "8rem" : "4rem" }} />
  </>
}