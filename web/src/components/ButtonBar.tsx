import { AppBar, Button, IconButton, LinearProgress, Toolbar, Tooltip, Typography } from "@mui/material";
import { useAppDispatch, useAppSelector } from "@/api";
import { socketActions, type SocketProgress } from "@/api/v1/socket/store";
import { tocActions } from "@/api/v1/toc/store";
import { ConfirmationDialog } from "./ConfirmationModal";
import { useState } from "react";

import EjectIcon from '@mui/icons-material/Eject';
import SaveAltIcon from '@mui/icons-material/SaveAlt';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import CancelIcon from '@mui/icons-material/Cancel';
import SettingsIcon from '@mui/icons-material/Settings';
import { StatusWrapper } from "./ButtonBar.styles";
import { endpoints, type ApiModel } from "@/api/endpoints";
import { ripActions } from "@/api/v1/rip/store";
import { uniqueFilter } from "@/util/array";
import { ConfigDialog } from "./modals/ConfigDialog";

type Props = {}

export const ButtonBar = ({ }: Props) => {
  const dispatch = useAppDispatch()

  const sortInfo = useAppSelector((state) => state.rip.sort_info)
  const library = useAppSelector((state) => state.rip.destination?.library)
  const media = useAppSelector((state) => state.rip.destination?.media)
  const content = useAppSelector((state) => state.rip.destination?.content)
  const socketRipState = useAppSelector((state) => state.socket.rip)
  const ripAll = useAppSelector((state) =>
    state.toc.source?.titles.length == [
      ...state.rip.sort_info.extra_indexes, 
      ...state.rip.sort_info.main_indexes
    ].filter(uniqueFilter).length
  )

  const tocLoading = useAppSelector((state) => state.toc.loading)

  const [cancelModalOpen, setCancelModalOpen] = useState<boolean>(false)
  const [configDialogOpen, setConfigDialogOpen] = useState<boolean>(false)

  let current_progress: SocketProgress | undefined
  if (socketRipState.current_title !== null && socketRipState.current_title !== undefined) {
    current_progress = socketRipState.current_progress?.[socketRipState.current_title]
  }

  const handleEject = () => {
    console.info('Ejecting disc')
    dispatch(socketActions.setSocketRipState())
    fetch(endpoints.disc.eject(), { method: 'GET' })
  }

  const handleLoadToc = () => {
    console.info('Fetching Toc')
    dispatch(tocActions.setTocLoading(true))
    dispatch(tocActions.setTocData(undefined))
    dispatch(socketActions.setSocketRipState())
    dispatch(ripActions.setMainIndexes([]))
    dispatch(ripActions.setExtraIndexes([]))
    fetch(endpoints.toc_async(), { method: 'GET' })
  }

  const handleCancelRip = () => {
    fetch(endpoints.rip.stop(), { method: 'GET' })
      .then((response) => response.json() as Promise<ApiModel['v1']['rip.stop']>)
      .then(({ status }) => {
        if (status === 'stopped') {
          dispatch(socketActions.updateSocketRipState({ started: false }))
        }
      })
  };

  const handleStartRip = () => {
    if (socketRipState?.started) {
      setCancelModalOpen(true)
    } else {
      dispatch(socketActions.setSocketRipState({ started: true }))
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

  const handleConfigDialogOpen = () => {
    setConfigDialogOpen(true)
  }

  const handleConfigDialogClose = () => {
    setConfigDialogOpen(false)
  }

  return <>
    <AppBar>
      <Toolbar>
        <Tooltip title="Menu">
          <IconButton
            onClick={handleConfigDialogOpen}
          >
            <SettingsIcon />
          </IconButton>
        </Tooltip>
        <Tooltip title="Eject Disc">
          <IconButton
            onClick={handleEject}
            disabled={socketRipState?.started}
          >
            <EjectIcon />
          </IconButton>
        </Tooltip>
        <Tooltip title="Load ToC (Table of Contents)">
          <IconButton
            onClick={handleLoadToc}
            disabled={socketRipState?.started}
            loading={tocLoading}
          >
            <SaveAltIcon />
          </IconButton>
        </Tooltip>
        <Button
          sx={{ marginLeft: "auto", textWrap: "nowrap", minWidth: 'max-content' }}
          onClick={handleStartRip}
          variant="outlined"
          startIcon={socketRipState?.started ? <CancelIcon /> : <CheckCircleIcon />}
        >
          {socketRipState?.started
            ? "Cancel Rip"
            : "Start Rip"
          }
        </Button>
      </Toolbar>
      {socketRipState?.total_status && <StatusWrapper>
        <Typography variant="caption">
          {socketRipState?.total_status
            ? <>{socketRipState.total_status} ({Math.round((socketRipState.total_progress?.progress ?? 0) * 10000) / 100}%) </>
            : "Status"
          } {socketRipState?.current_status && current_progress && <>
            / {socketRipState.current_status} ({Math.round((current_progress.progress ?? 0) * 10000) / 100}%)
          </>
          }
        </Typography>
        <LinearProgress
          variant="buffer"
          value={socketRipState?.total_progress?.progress ? socketRipState.total_progress.progress * 100 : 0}
          valueBuffer={socketRipState?.total_progress?.buffer ? socketRipState.total_progress.buffer * 100 : 0}
        />
        {socketRipState?.current_status && current_progress && <>
          <LinearProgress
            variant="buffer"
            valueBuffer={(current_progress.buffer ?? 1) * 100}
            value={(current_progress.progress ?? 0) * 100}
          />
        </>}
      </StatusWrapper>}
    </AppBar>
    <ConfirmationDialog
      open={cancelModalOpen}
      onClose={() => { setCancelModalOpen(false) }}
      onConfirm={() => { handleCancelRip() }}
      title={'Cancel Rip?'}
      message={'This disc will not get uploaded if it is cancelled now'}
    />
    <ConfigDialog
      open={configDialogOpen}
      onClose={handleConfigDialogClose}
    />
    <div style={{ height: socketRipState?.total_status ? "8rem" : "4rem" }} />
  </>
}