import { useAppDispatch, useAppSelector } from "@/api/store"
import { ripActions } from "@/api/store/rip"
import { hmsToSeconds } from "@/util/string"
import { Box, Card, Checkbox, CircularProgress, Collapse, Divider, IconButton, LinearProgress, Radio, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Typography } from "@mui/material"
import { useEffect, useState } from "react"
import type { TitleInfo, Toc } from "@/api/store/toc"

import ExpandLessIcon from '@mui/icons-material/ExpandLess';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import type { SocketProgress } from "@/api/store/socket"
import { isCompleteEnough, isRippingStatus } from "../socket/Connection"
import { BorderCell, CheckboxCell, CollapseRow, DetailsWrapper, DividerCell, EpisodeCell, FilenameCell, FilenameContent, FilenameHead, MainExtraCell, MainExtrasRadioGroup, RuntimeCell, StatusWrapper, StatusWrapperCell, TOCGridContainer } from "./TOCGrid.styles"

import KeyboardDoubleArrowDownIcon from '@mui/icons-material/KeyboardDoubleArrowDown';

type Props = {
  data?: Toc
  loading?: boolean
}

type TitleGroup = {
  title: TitleInfo,
  index: number,
  matches: number[]
}

const EPISODE_LENGTH_TOLERANCE_SECONDS = 120

const episodeId = (seasonNumber: number, episodeNumber: number) => {
  return "S" + `${seasonNumber}`.padStart(2, "0") + "E" + `${episodeNumber}`.padStart(2, "0")
}

export const TOCGrid = ({ }: Props) => {

  const dispatch = useAppDispatch()

  const data = useAppSelector((state) => state.toc)
  const mainIndexes = useAppSelector((state) => state.rip.sort_info.main_indexes)
  const extraIndexes = useAppSelector((state) => state.rip.sort_info.extra_indexes)
  const content = useAppSelector((state) => state.rip.destination.content)
  const ripState = useAppSelector((state) => state.socket.ripState)

  let current_progress: SocketProgress | undefined
  if (ripState.current_title !== null && ripState.current_title !== undefined) {
    current_progress = ripState.current_progress?.[ripState.current_title]
  }

  // const [oldMainIndexes, setOldMainIndexes] = useState<number[]>([])
  const [oldExtraIndexes, setOldExtraIndexes] = useState<number[]>([])

  const getTitleGroups = () => {
    const titleGroups: TitleGroup[] = []

    const matchedIndexes = () => (titleGroups.map((titleGroup) => (
      titleGroup.matches
    )).flat())

    data?.source?.titles.forEach((outerTitle, outerIndex) => {
      const newTitleGroup: TitleGroup = { title: outerTitle, index: outerIndex, matches: [outerIndex] }
      const outerTitleLength = hmsToSeconds(outerTitle.runtime)
      data?.source?.titles.forEach((innerTitle, innerIndex) => {
        if (
          !(innerIndex in matchedIndexes())
          && hmsToSeconds(innerTitle.runtime) > outerTitleLength - EPISODE_LENGTH_TOLERANCE_SECONDS
          && hmsToSeconds(innerTitle.runtime) < outerTitleLength + EPISODE_LENGTH_TOLERANCE_SECONDS

        ) {
          newTitleGroup.matches.push(innerIndex)
        }
      })
      titleGroups.push(newTitleGroup)
    })

    if (titleGroups.length > 0) {
      return {
        titleGroups: titleGroups,
        longestTitleGroup: titleGroups.reduce((previous, current) => {
          if (hmsToSeconds(previous.title.runtime) < hmsToSeconds(current.title.runtime)) {
            return current
          } else {
            return previous
          }
        }),
        biggestTitleGroup: titleGroups.reduce((previous, current) => {
          if (previous.matches.length < current.matches.length) {
            return current
          } else {
            return previous
          }
        })
      }
    }

    return {
      titleGroups: undefined,
      longestTitleGroup: undefined,
      biggestTitleGroup: undefined
    }
  }

  const getIndexes = () => {
    const { biggestTitleGroup, longestTitleGroup } = getTitleGroups()
    const activeTitleGroup = content === "show" ? biggestTitleGroup : longestTitleGroup

    const mainIndexes = []
    const extraIndexes = []

    if (activeTitleGroup) {
      for (let i = 0; i < (data?.source?.titles.length ?? 0); i++) {
        if (activeTitleGroup.matches.indexOf(i) > -1) {
          mainIndexes.push(i)
        } else {
          extraIndexes.push(i)
        }
      }
    }

    return { mainIndexes, extraIndexes }
  }

  const setIndexes = async () => {
    const { mainIndexes, extraIndexes } = getIndexes()
    dispatch(ripActions.setMainIndexes(mainIndexes))
    dispatch(ripActions.setExtraIndexes(extraIndexes))
  }

  useEffect(() => {
    const makeItAsync = async () => {
      if (data && !ripState?.rip_started) {
        dispatch(ripActions.setTocLength(data?.source?.titles.length));
        setIndexes();
      }
    }

    makeItAsync()
  }, [data, content])

  const handleSelectAllOnClick = (_event: React.ChangeEvent, checked: boolean) => {
    if (checked) {
      data?.source?.titles.forEach((_value, index) => {
        const isInMainIndexes = (mainIndexes.indexOf(index) > -1)
        const isInExtraIndexes = (extraIndexes.indexOf(index) > -1)
        // const wasInMainIndexes = (oldMainIndexes.indexOf(index) > -1)
        const wasInExtraIndexes = (oldExtraIndexes.indexOf(index) > -1)
        if (!isInMainIndexes && !isInExtraIndexes) {
          if (wasInExtraIndexes) dispatch(ripActions.addExtraIndex(index))
          else dispatch(ripActions.addMainIndex(index))
        }
      });
      // setOldMainIndexes([])
      setOldExtraIndexes([])
    } else {
      setOldExtraIndexes(extraIndexes)
      dispatch(ripActions.setMainIndexes([]))
      dispatch(ripActions.setExtraIndexes([]))
    }
  }

  return (<>
    {ripState?.total_status && <>
      <Card>
        <StatusWrapper>
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
        </StatusWrapper>
      </Card>
    </>}
    <Card>
      <TOCGridContainer>
        <BorderCell />
        <CheckboxCell>
          <IconButton>
            <KeyboardDoubleArrowDownIcon />
          </IconButton>
        </CheckboxCell>
        <CheckboxCell>
          <Checkbox onChange={handleSelectAllOnClick} />
        </CheckboxCell>
        <CheckboxCell>
          <Typography variant="body2">
            #
          </Typography>
        </CheckboxCell>
        <MainExtraCell>
          <Typography variant="body2"
            style={{
              display: "flex",
              justifyContent: "flex-start",
              gap: "10px",
            }}
          >
            <div>
              Main
            </div>
            <Divider orientation="vertical" flexItem />
            <div>
              Extra
            </div>
          </Typography>
        </MainExtraCell>
        {content === "show" &&
          <EpisodeCell>
            <Typography variant="body2">Episode(s)</Typography>
          </EpisodeCell>
        }
        <RuntimeCell><Typography variant="body2">Runtime</Typography></RuntimeCell>
        <FilenameCell>
          <FilenameHead>
            <Typography variant="body2">
              Filename
            </Typography>
          </FilenameHead>
        </FilenameCell>
        {data
          ? (
            data?.source?.titles.map((title, index) => {
              return (
                <>
                  <DividerCell/>
                  <TOCGridRow
                    key={index}
                    index={index}
                    data={title}
                    progress={ripState?.current_progress?.[index]?.progress ?? undefined}
                    buffer={ripState?.current_progress?.[index]?.buffer ?? undefined}
                    statusText={index === ripState?.current_title ? ripState?.current_status : ''}
                    titleType={
                      mainIndexes.indexOf(index) > -1
                        ? "main"
                        : extraIndexes.indexOf(index) > -1
                          ? "extra"
                          : undefined
                    }
                    episodeNumber={mainIndexes.indexOf(index)}
                  />
                </>
              )
            })
          ) : (
            <TableRow>
              <TableCell colSpan={5}>No data</TableCell>
            </TableRow>
          )
        }
        <BorderCell />
      </TOCGridContainer>
    </Card>
  </>)
}

type RowProps = {
  index: number;
  data: TitleInfo;
  progress?: number;
  buffer?: number;
  statusText?: string;
  titleType?: "main" | "extra";
  episodeNumber?: number;
  minimized?: boolean
}

export const TOCGridRow = ({ index, data, statusText, titleType, episodeNumber, minimized: minimizedProp }: RowProps) => {
  const dispatch = useAppDispatch()

  const [minimized, setMinimized] = useState<boolean>(minimizedProp ?? true)

  const seasonNumber = useAppSelector((state) => state.rip.sort_info.season_number)
  const firstEpisode = useAppSelector((state) => state.rip.sort_info.first_episode)
  const splitSegments = useAppSelector((state) => state.rip.sort_info.split_segments)
  const content = useAppSelector((state) => state.rip.destination.content)
  const ripStarted = useAppSelector((state) => state.socket.ripState.rip_started)
  const currentProgress = useAppSelector((state) => state.socket.ripState.current_progress?.[index])

  const progress = currentProgress?.progress
  const buffer = currentProgress?.buffer

  const isMain = titleType === "main"
  // const isExtra = titleType === "extra"
  const isSelected = titleType !== undefined
  // const isMovie = content === "movie"
  const isShow = content === "show"
  const isRippingTitle = isRippingStatus(statusText)

  let rowEpisodeNumber: number | undefined
  let episodeString: string | undefined

  if (
    isShow && isMain && seasonNumber && firstEpisode &&
    episodeNumber !== undefined &&
    episodeNumber !== null
    && episodeNumber > -1
  ) {
    rowEpisodeNumber = firstEpisode + (episodeNumber * (splitSegments && splitSegments.length > 0 ? splitSegments.length : 1))
    episodeString = episodeId(seasonNumber, firstEpisode + episodeNumber)
  }

  const [wasMain, setWasMain] = useState<boolean>(!isSelected ? true : isMain)

  const handleCheckboxOnChange = (_event: React.ChangeEvent, checked: boolean) => {
    if (checked) {
      if (wasMain) {
        dispatch(ripActions.addMainIndex(index))
      } else {
        dispatch(ripActions.addExtraIndex(index))
      }
    } else {
      if (isMain) {
        dispatch(ripActions.removeMainIndex(index))
        setWasMain(true)
      } else {
        dispatch(ripActions.removeExtraIndex(index))
        setWasMain(false)
      }
    }
  }

  const handleRadioButtonChange = (_event: React.ChangeEvent, value: string) => {
    if (value === "main") {
      dispatch(ripActions.addMainIndex(index))
      dispatch(ripActions.removeExtraIndex(index))
    } else { // value === "extra"
      dispatch(ripActions.addExtraIndex(index))
      dispatch(ripActions.removeMainIndex(index))
    }
  }

  return <>
    <CheckboxCell>
      <IconButton
        onClick={() => {
          setMinimized((prev) => !prev)
        }}
      >
        {minimized
          ? <ExpandMoreIcon />
          : <ExpandLessIcon />
        }
      </IconButton>
    </CheckboxCell>
    <CheckboxCell>
      <Checkbox disabled={ripStarted} checked={isSelected} onChange={handleCheckboxOnChange} />
    </CheckboxCell>
    <CheckboxCell>
      {index}
    </CheckboxCell>
    <MainExtraCell>
      <MainExtrasRadioGroup
        row
        aria-labelledby="demo-radio-buttons-group-label"
        value={
          isSelected
            ? (isMain ? "main" : "extra")
            : null
        }
        name="radio-buttons-group"
        onChange={handleRadioButtonChange}
        aria-disabled={!isSelected}
        sx={{ display: "inline-block" }}
      >
        <Radio disabled={!isSelected || ripStarted} aria-label="extra" value="main" />
        <Divider orientation="vertical" flexItem />
        <Radio disabled={!isSelected || ripStarted} aria-label="extra" value="extra" />
      </MainExtrasRadioGroup>
    </MainExtraCell>
    {isShow && <EpisodeCell><Typography variant="body2">{
      (splitSegments && splitSegments.length > 0 && seasonNumber && rowEpisodeNumber)
        ? splitSegments.map((_, index) => (episodeId(seasonNumber, rowEpisodeNumber + index))).join(' ')
        : episodeString

    }</Typography></EpisodeCell>}
    <RuntimeCell><Typography variant="body2">
      {data.runtime}
    </Typography></RuntimeCell>
    <FilenameCell>
      <FilenameContent>
        <Typography variant="body2" sx={{ display: "inline-block" }}>
          {data.filename}
        </Typography>
        <Collapse in={minimized}>
          {progress !== undefined && progress !== null && minimized && <>
            <Typography variant="subtitle2" fontSize={12} color={"textDisabled"}>
                {isCompleteEnough(progress) ? "Complete" : `${statusText} (${Math.round(progress * 10000) / 100}%)`}
            </Typography>
          </>}
        </Collapse>
      </FilenameContent>
    </FilenameCell>
    <CollapseRow in={!minimized}>
      <DetailsWrapper>
        <Box>
            <span><Typography variant="caption">
              Chapters: {data.chapters}
            </Typography></span>
            <span><Typography variant="caption">
              Segments: {data.segments}
            </Typography></span>
            <span><Typography variant="caption">
              Segments Map: {data.segments_map.split(",").join(", ")}
            </Typography></span>
        </Box>
        {progress !== undefined && progress !== null && <>
          <StatusWrapperCell>
            <Typography variant="caption">{isCompleteEnough(progress) ? "Complete" : statusText ?? ''}</Typography>
            {isSelected
              ? <LinearProgress variant={buffer !== undefined ? "buffer" : "determinate"} value={progress ? progress * 100 : 0} valueBuffer={(buffer ? buffer * 100 : buffer) ?? undefined} />
              : <LinearProgress variant="determinate" value={0} color="secondary" />
            }
          </StatusWrapperCell>
        </>}
      </DetailsWrapper>
    </CollapseRow>
  </>
}