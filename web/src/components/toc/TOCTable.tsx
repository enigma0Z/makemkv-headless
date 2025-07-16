import { useAppDispatch, useAppSelector } from "@/api/store"
import { ripActions } from "@/api/store/rip"
import { hmsToSeconds } from "@/util/string"
import { Box, Card, Checkbox, Collapse, Divider, FormControlLabel, IconButton, Input, LinearProgress, Radio, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, TextField } from "@mui/material"
import { useContext, useEffect, useState } from "react"
import { MainExtrasRadioGroup, MobileOnlyTableRow, ProgressCell, ProgressCellHeader, StatusWrapper, StyledTableCellBottom, StyledTableCellMiddle, StyledTableCellTop } from "./TOCTable.styles"
import { Context } from "../socket/Context"
import type { TitleInfo, Toc } from "@/api/store/toc"

import ExpandLessIcon from '@mui/icons-material/ExpandLess';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';

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

// export const TOCTable = ({ data = undefined, loading = false }: Props) => {
export const TOCTable = ({ }: Props) => {
  console.debug('TOCTable render()')

  const dispatch = useAppDispatch()

  const { ripState } = useContext(Context)

  const current_progress = ripState?.current_title !== undefined ? ripState?.current_progress?.[ripState.current_title] : undefined

  const data = useAppSelector((state) => state.toc)
  const mainIndexes = useAppSelector((state) => state.rip.sort_info.main_indexes)
  const extraIndexes = useAppSelector((state) => state.rip.sort_info.extra_indexes)
  const content = useAppSelector((state) => state.rip.destination.content)

  const [oldMainIndexes, setOldMainIndexes] = useState<number[]>([])
  const [oldExtraIndexes, setOldExtraIndexes] = useState<number[]>([])

  const getLongestTitle = () => {
    let longestTitleIndex = 0
    let longestTitleLength = 0
    data?.source?.titles.forEach((title, index) => {
      const outerTitleLength = hmsToSeconds(title.runtime)
      if (outerTitleLength > longestTitleLength) {
        longestTitleLength = outerTitleLength
        longestTitleIndex = index
      }
    })

    return {
      longestTitleLength,
      longestTitleIndex
    }
  }

  const getTitleGroups = () => {
    console.debug('getTitleGroups()')
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
      console.debug('getIndexes for', content, activeTitleGroup)
      for (let i=0; i < (data?.source?.titles.length ?? 0); i++) {
        if (activeTitleGroup.matches.indexOf(i) > -1) {
          mainIndexes.push(i)
        } else {
          extraIndexes.push(i)
        }
      }
    }

    return {mainIndexes, extraIndexes}
  }

  const setIndexes = async () => {
    const {mainIndexes, extraIndexes} = getIndexes()
    dispatch(ripActions.setMainIndexes(mainIndexes))
    dispatch(ripActions.setExtraIndexes(extraIndexes))
  }

  useEffect(() => {
    const makeItAsync = async () => {
      console.debug('makeItAsync()')
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
        const wasInMainIndexes = (oldMainIndexes.indexOf(index) > -1)
        const wasInExtraIndexes = (oldExtraIndexes.indexOf(index) > -1)
        if (!isInMainIndexes && !isInExtraIndexes) {
          if (wasInExtraIndexes) dispatch(ripActions.addExtraIndex(index))
          else dispatch(ripActions.addMainIndex(index))
        }
      });
      setOldMainIndexes([])
      setOldExtraIndexes([])
    } else {
      setOldMainIndexes(mainIndexes)
      setOldExtraIndexes(extraIndexes)
      dispatch(ripActions.setMainIndexes([]))
      dispatch(ripActions.setExtraIndexes([]))
    }
  }
  
  return (<>
    <Card>
      <TableContainer>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell width="1%" sx={{ paddingRight: 0 }} >
              </TableCell>
              <TableCell width="1%" sx={{ paddingLeft: 0, paddingRight: 0 }}>
                <Checkbox onChange={handleSelectAllOnClick} />
              </TableCell>
              <TableCell width="1%">#</TableCell>
              <TableCell width="1%">
                <div
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
                </div>
              </TableCell>
              { content === "show" && <TableCell width="1%">Episode</TableCell> }
              <TableCell width="1%">Runtime</TableCell>
              <TableCell width="1%">Filename</TableCell>
              <ProgressCellHeader width="60%">
                  <StatusWrapper>
                  { ripState?.total_status && <>
                        <div>
                          { ripState?.total_status 
                            ? <>{ripState.total_status} ({ Math.round( (ripState.total_progress?.progress ?? 0) * 100) }%) </>
                            : "Status"
                          } { ripState?.current_status && current_progress && <>
                              / {ripState.current_status} ({ Math.round(current_progress.progress * 100) }%)
                            </>
                          }
                        </div>
                        <LinearProgress 
                          variant="buffer" 
                          value={ripState?.total_progress?.progress ? ripState.total_progress.progress * 100 : 0} 
                          valueBuffer={ripState?.total_progress?.buffer ? ripState.total_progress.buffer * 100 : 0 }
                        />
                        { ripState?.current_status && current_progress && <>
                          <LinearProgress
                            variant="buffer"
                            valueBuffer={ (current_progress.buffer ?? 1) * 100 }
                            value={ current_progress.progress * 100 }
                          />
                        </>}
                    </>
                  }
                  </StatusWrapper>
              </ProgressCellHeader>
            </TableRow>
            <MobileOnlyTableRow>
              <TableCell colSpan={6}>
                <StatusWrapper>
                  { ripState?.total_status && <>
                        <div>
                          {ripState?.total_status ?? "Status"}
                        </div>
                        <LinearProgress 
                          variant="buffer" 
                          value={ripState?.total_progress?.progress ? ripState.total_progress.progress * 100 : 0} 
                          valueBuffer={ripState?.total_progress?.buffer ? ripState.total_progress.buffer * 100 : 0} 
                        />
                    </>
                  }
                </StatusWrapper> 
              </TableCell>
            </MobileOnlyTableRow>
          </TableHead>
          <TableBody>
            { data 
              ? (
                data?.source?.titles.map((title, index) => {
                  return (
                    <TOCRow 
                      key={index} 
                      index={index} 
                      data={title} 
                      // progress={(ripState?.current_progress?.[index]?.progress)}
                      // buffer={ripState?.current_progress?.[index]?.buffer}
                      // statusText={index === ripState?.current_title ? ripState?.current_status : ''}
                      titleType={
                        mainIndexes.indexOf(index) > -1 
                        ? "main" 
                        : extraIndexes.indexOf(index) > -1 
                          ? "extra"
                          : undefined
                      }
                      episodeNumber={mainIndexes.indexOf(index)}
                    />
                  )
                })
              ) : (
                <TableRow>
                  <TableCell colSpan={5}>No data</TableCell>
                </TableRow>
              )
            }
          </TableBody>
        </Table>
      </TableContainer>
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
}

export const TOCRow = ({ index, data, progress, buffer, statusText, titleType, episodeNumber }: RowProps) => {
  console.debug('TOCRow render()')

  const dispatch = useAppDispatch()

  const [minimized, setMinimized] = useState<boolean>(false)
  const [segments, setSegments] = useState<string | null>(null)

  const { ripState } = useContext(Context)

  // const mainIndexes = useAppSelector((state) => state.rip.sort_info.main_indexes)
  // const extraIndexes = useAppSelector((state) => state.rip.sort_info.extra_indexes)
  const seasonNumber = useAppSelector((state) => state.rip.sort_info.season_number)
  const firstEpisode = useAppSelector((state) => state.rip.sort_info.first_episode)
  const splitSegments = useAppSelector((state) => state.rip.sort_info.split_segments)
  const content = useAppSelector((state) => state.rip.destination.content)

  const isMain = titleType === "main"
  const isExtra = titleType === "extra"
  const isSelected = titleType !== undefined
  const isMovie = content === "movie"
  const isShow = content === "show"

  let rowEpisodeNumber: number | undefined
  let episodeString: string | undefined

  if (isShow && isMain && seasonNumber && firstEpisode && episodeNumber && episodeNumber > -1) {
    rowEpisodeNumber = firstEpisode + ( episodeNumber * ( splitSegments && splitSegments.length > 0 ? splitSegments.length : 1 ) )
    episodeString = episodeId(seasonNumber, firstEpisode + episodeNumber)
  }

  const [wasMain, setWasMain] = useState<boolean>(!isSelected ? true : isMain)

  const handleCheckboxOnChange = (event: React.ChangeEvent, checked: boolean) => {
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
    <TableRow>
      <StyledTableCellTop size="small" sx={{ paddingRight: 0}}>
        <IconButton 
          onClick={() => {
            setMinimized((prev) => !prev)
          }}
        >
          { minimized
            ? <ExpandMoreIcon />
            : <ExpandLessIcon />
          }
        </IconButton> 
      </StyledTableCellTop>
      <StyledTableCellTop sx={{ paddingRight: 0, paddingLeft: 0}}>
        <Checkbox disabled={ ripState?.rip_started } checked={isSelected} onChange={handleCheckboxOnChange} />
      </StyledTableCellTop>
      <StyledTableCellTop>{index}</StyledTableCellTop>
      <StyledTableCellTop>
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
          sx={{display: "inline-block"}}
        >
          <Radio disabled={!isSelected || ripState?.rip_started} aria-label="extra" value="main" />
          <Divider orientation="vertical" flexItem />
          <Radio disabled={!isSelected || ripState?.rip_started} aria-label="extra" value="extra" />
        </MainExtrasRadioGroup>
      </StyledTableCellTop>
      { isShow && <StyledTableCellTop>{
        splitSegments && splitSegments.length > 0 && seasonNumber && rowEpisodeNumber
        ? splitSegments.map((_, index) => (episodeId(seasonNumber, rowEpisodeNumber + index))).join(' ')
        : episodeString
        
      }</StyledTableCellTop> }
      <StyledTableCellTop>{data.runtime}</StyledTableCellTop>
      <StyledTableCellTop>{data.filename}</StyledTableCellTop>
      <ProgressCell>
        { progress !== undefined && <>
            <div>{progress > .98 ? "Complete" : <>{statusText} ({ Math.round(progress*100) }%)</>}</div>
            { isSelected
              ? <LinearProgress variant={buffer !== undefined ? "buffer" : "determinate"} value={progress ? progress * 100 : 0} valueBuffer={buffer ? buffer * 100 : buffer} />
              : <LinearProgress variant="determinate" value={0} color="secondary" />
            }
        </> }
      </ProgressCell>
    </TableRow>
    <TableRow><StyledTableCellMiddle colSpan={8}>
      <Collapse in={!minimized}>
        <Box>
          <span>Chapters: {data.chapters}</span>
          <span>Segments: {data.segments}</span>
          <span>Segments Map: {data.segments_map.split(",").join(", ")}</span>
        </Box>
      </Collapse>
    </StyledTableCellMiddle></TableRow>
    <MobileOnlyTableRow><StyledTableCellBottom colSpan={8}>
          <StatusWrapper>
            { progress !== undefined && <>
                <div>{progress > .98 ? "Complete" : statusText ?? ''}</div>
                { isSelected
                  ? <LinearProgress variant={buffer !== undefined ? "buffer" : "determinate"} value={progress ? progress * 100 : 0} valueBuffer={buffer ? buffer * 100 : buffer} />
                  : <LinearProgress variant="determinate" value={0} color="secondary" />
                }
            </> }
          </StatusWrapper>
    </StyledTableCellBottom></MobileOnlyTableRow>
  </>
}