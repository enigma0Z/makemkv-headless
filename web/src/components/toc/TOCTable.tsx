import { useAppDispatch, useAppSelector } from "@/api/store"
import { ripActions } from "@/api/store/rip"
import { hmsToSeconds } from "@/util/string"
import { Card, Checkbox, FormControlLabel, LinearProgress, Radio, Table, TableBody, TableCell, TableContainer, TableHead, TableRow } from "@mui/material"
import { useContext, useEffect, useState } from "react"
import { MainExtrasRadioGroup, StatusContentWrapper, StatusContentWrapperLeft, StatusWrapper, WidgetCell } from "./TOCTable.styles"
import { Context } from "../socket/Context"
import type { TitleInfo, Toc } from "@/api/store/toc"

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

// export const TOCTable = ({ data = undefined, loading = false }: Props) => {
export const TOCTable = ({ }: Props) => {
  const dispatch = useAppDispatch()

  const { ripState } = useContext(Context)

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

  const getLongestTitleGroup = () => {
    const titleGroups: TitleGroup[] = []

    const matchedIndexes = () => (titleGroups.map((titleGroup) => (
      titleGroup.matches
    )).flat())

    data?.source?.titles.forEach((outerTitle, outerIndex) => {
      const newTitleGroup: TitleGroup = { title: outerTitle, index: outerIndex, matches: [] }
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
      longestTItleGroup: undefined
    }
  }

  const getMovieIndexes = () => {
    const { longestTitleIndex } = getLongestTitle()
    const mainIndexes = []
    const extraIndexes = []
    for (let i=0; i < (data?.source?.titles.length ?? 0); i++) {
      if (i == longestTitleIndex) {
        mainIndexes.push(i)
      } else {
        extraIndexes.push(i)
      }
    }
    return {mainIndexes, extraIndexes}
  }
  
  const getShowIndexes = () => {
    const {longestTitleGroup} = getLongestTitleGroup()
    const mainIndexes = []
    const extraIndexes = []
    for (let i=0; i < (data?.source?.titles.length ?? 0); i++) {
      if (longestTitleGroup?.matches.indexOf(i) ?? -1 > -1) {
        mainIndexes.push(i)
      } else {
        extraIndexes.push(i)
      }
    }
    return {mainIndexes, extraIndexes}
  }

  const setIndexes = () => {
    if (content === "movie") {
      const {mainIndexes, extraIndexes} = getMovieIndexes()
      dispatch(ripActions.setMainIndexes(mainIndexes))
      dispatch(ripActions.setExtraIndexes(extraIndexes))
    } else if ( content === "show" ) {
      const {mainIndexes, extraIndexes} = getShowIndexes()
      dispatch(ripActions.setMainIndexes(mainIndexes))
      dispatch(ripActions.setExtraIndexes(extraIndexes))
    }
  }

  useEffect(() => {
    if (data) {
      dispatch(ripActions.setTocLength(data?.source?.titles.length));
      setIndexes();
    }
  }, [data]) 


  useEffect(() => { data && setIndexes() }, [content])

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
              <TableCell
                padding="checkbox"
                size="small"
              ><Checkbox 
                onChange={handleSelectAllOnClick}
              /></TableCell>
              <WidgetCell>#</WidgetCell>
              <TableCell width="75%">
                <StatusContentWrapper>
                  <StatusContentWrapperLeft>
                    Type
                  </StatusContentWrapperLeft>
                  <StatusWrapper>
                  { ripState?.total_status && <>
                        <div>
                          {ripState?.total_status}
                        </div>
                        <LinearProgress 
                          variant="buffer" 
                          value={ripState?.total_progress?.progress ? ripState.total_progress.progress * 100 : 0} 
                          valueBuffer={ripState?.total_progress?.buffer ? ripState.total_progress.buffer * 100 : 0} 
                        />
                    </>
                  }
                  </StatusWrapper>
                </StatusContentWrapper>
              </TableCell>
              <TableCell width="10%">Runtime</TableCell>
              <TableCell width="15%">Filename</TableCell>
            </TableRow>
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
                      progress={(ripState?.current_progress && ripState.current_progress[index]?.progress) ?? undefined}
                      buffer={ripState?.current_progress?.[index]?.buffer}
                      statusText={index === ripState?.current_title ? ripState?.current_status : ''}
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
}

export const TOCRow = ({ index, data, progress, buffer, statusText }: RowProps) => {
  const dispatch = useAppDispatch()

  const mainIndexes = useAppSelector((state) => state.rip.sort_info.main_indexes)
  const extraIndexes = useAppSelector((state) => state.rip.sort_info.extra_indexes)

  const isMain = mainIndexes.indexOf(index) > -1
  const isExtra = extraIndexes.indexOf(index) > -1
  const isSelected = isMain || isExtra

  const [wasMain, setWasMain] = useState<boolean>(!isSelected ? true : isMain)

  const handleCheckboxOnChange = (event: React.ChangeEvent, checked: boolean) => {
    console.log('handleCheckboxOnChange(), event, checked', event, checked)
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

  return <TableRow>
    <TableCell
      padding="checkbox"

    ><Checkbox 
      checked={isSelected}
      onChange={handleCheckboxOnChange}
    /></TableCell>
    <TableCell>{index}</TableCell>
    <TableCell>
      <StatusContentWrapper>
        <StatusContentWrapperLeft>
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
            <FormControlLabel disabled={!isSelected} value="main" control={<Radio />} label="Main" />
            <FormControlLabel disabled={!isSelected} value="extra" control={<Radio />} label="Extra" />
          </MainExtrasRadioGroup>
        </StatusContentWrapperLeft>
        <StatusWrapper>
          { progress !== undefined && <>
              <div>{progress > .98 ? "Complete" : statusText ?? ''}</div>
              { isSelected
                ? <LinearProgress variant={buffer !== undefined ? "buffer" : "determinate"} value={progress ? progress * 100 : 0} valueBuffer={buffer ? buffer * 100 : buffer} />
                : <LinearProgress variant="determinate" value={0} color="secondary" />
              }
          </> }
        </StatusWrapper>
      </StatusContentWrapper>
    </TableCell>
    <TableCell>{data.runtime}</TableCell>
    <TableCell>{data.filename}</TableCell>
  </TableRow>
}