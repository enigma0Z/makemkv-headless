import { useAppDispatch, useAppSelector } from "@/api/store"
import { ripActions } from "@/api/store/rip"
import type { TitleInfo, Toc } from "@/api/types/Toc"
import { hmsToSeconds } from "@/util/string"
import { Card, Checkbox, FormControlLabel, LinearProgress, Radio, RadioGroup, Table, TableBody, TableCell, TableContainer, TableHead, TableRow } from "@mui/material"
import { useContext, useEffect, useState } from "react"
import { MainExtrasRadioGroup, StatusWrapper, WidgetCell, WidgetWrapper } from "./TOCTable.styles"
import { Context, type RipStartMessageEvent } from "../socket/Context"
import { takeGreater } from "@/util/number"

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

export const TOCTable = ({ data = undefined, loading = false }: Props) => {
  const dispatch = useAppDispatch()

  const { 
    progressMessageEvents, setProgressMessageEvents,
    progressValueMessageEvents, setProgressValueMessageEvents,
    ripStartMessageEvents, setRipStartMessageEvents
  } = useContext(Context)

  const mainIndexes = useAppSelector((state) => state.rip.sort_info.main_indexes)
  const extraIndexes = useAppSelector((state) => state.rip.sort_info.extra_indexes)
  const content = useAppSelector((state) => state.rip.destination.content)

  const [oldMainIndexes, setOldMainIndexes] = useState<number[]>([])
  const [oldExtraIndexes, setOldExtraIndexes] = useState<number[]>([])

  const [completedIndexes, setCompletedIndexes] = useState<number[]>([])
  const [previousIndex, setPreviousIndex] = useState<number>()

  const [completed, setCompleted] = useState<boolean>(false)

  const currentProgressEvents = (progressMessageEvents && progressMessageEvents.filter((event) => event.progressType === "Current")) ?? []
  const totalProgressEvents = (progressMessageEvents && progressMessageEvents.filter((event) => event.progressType === "Total")) ?? []

  const latestProgressValueEvent = progressValueMessageEvents && progressValueMessageEvents[progressValueMessageEvents.length-1]

  const latestCurrentProgressEvent = currentProgressEvents[currentProgressEvents.length-1]
  const latestTotalProgressEvent = totalProgressEvents[totalProgressEvents.length-1]

  const latestRipStartEvent: RipStartMessageEvent | undefined = ripStartMessageEvents?.[ripStartMessageEvents.length-1]

  let currentIndex: number | undefined = undefined

  if (
    ( latestRipStartEvent === undefined 
      && latestTotalProgressEvent?.name === "Saving all titles to MKV files"
    ) || loading
  ) {
    console.log("Resetting rip status", latestRipStartEvent, latestTotalProgressEvent, loading)
    if (completedIndexes.length !== 0) setCompletedIndexes([]);
    if (previousIndex !== undefined) setPreviousIndex(undefined);
    if (completed) setCompleted(false);

    if (
      setRipStartMessageEvents 
      && (ripStartMessageEvents?.length ?? -1) > 0
    ) setRipStartMessageEvents(() => [])

    if (
      setProgressMessageEvents 
      && (progressMessageEvents?.length ?? -1) > 0
    ) setProgressMessageEvents(() => [])

    if (
      setProgressValueMessageEvents 
      && (progressValueMessageEvents?.length ?? -1) > 0
    ) setProgressValueMessageEvents(() => [])
  } else if(
    latestCurrentProgressEvent?.name === "Analyzing seamless segments" 
    || latestCurrentProgressEvent?.name === "Saving to MKV file" 
  ) {
    currentIndex = takeGreater(latestRipStartEvent?.index, latestCurrentProgressEvent?.index)
    console.log("Current Index", currentIndex)
    if (
      currentIndex !== undefined
      && completedIndexes.indexOf(currentIndex) === -1
      && latestCurrentProgressEvent.name === "Saving to MKV file" 
      && ((
        latestProgressValueEvent
        && latestProgressValueEvent.current / latestProgressValueEvent.max > 0.98
      ) || (
        previousIndex !== currentIndex
      ))
    ) {
      setCompletedIndexes((prev) => 
        currentIndex !== undefined ? [...prev, currentIndex] : prev
      )
    }

    if (previousIndex !== currentIndex) {
      setPreviousIndex(currentIndex)
    }
  }

  const getLongestTitle = () => {
    let longestTitleIndex = 0
    let longestTitleLength = 0
    data?.source.titles.forEach((title, index) => {
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
    /**
     * [
     *   title: TitleInfo
     *   index: number
     *   matches: TitleInfo[]
     * ]
     */
    const titleGroups: TitleGroup[] = []

    const matchedIndexes = () => (titleGroups.map((titleGroup) => (
      titleGroup.matches
    )).flat())

    data?.source.titles.forEach((outerTitle, outerIndex) => {
      const newTitleGroup: TitleGroup = { title: outerTitle, index: outerIndex, matches: [] }
      const outerTitleLength = hmsToSeconds(outerTitle.runtime)
      data.source.titles.forEach((innerTitle, innerIndex) => {
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

  const getMovieIndexes = () => {
    const { longestTitleIndex } = getLongestTitle()
    const mainIndexes = []
    const extraIndexes = []
    for (let i=0; i < (data?.source.titles.length ?? 0); i++) {
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
    for (let i=0; i < (data?.source.titles.length ?? 0); i++) {
      if (longestTitleGroup.matches.indexOf(i) > -1) {
        mainIndexes.push(i)
      } else {
        extraIndexes.push(i)
      }
    }
    return {mainIndexes, extraIndexes}
  }

  useEffect(() => {
    if (data) {
      dispatch(ripActions.setTocLength(data.source.titles.length))

      let longestTitleIndex = 0
      let longestTitleLength = 0
      data.source.titles.forEach((title, index) => {
        const outerTitleLength = hmsToSeconds(title.runtime)
        if (outerTitleLength > longestTitleLength) {
          longestTitleLength = outerTitleLength
          longestTitleIndex = index
        }
      })

      let getIndexes: () => { mainIndexes: number[], extraIndexes: number[] }
      if (content === "movie") getIndexes = getMovieIndexes
      else getIndexes = getShowIndexes

      const {mainIndexes, extraIndexes} = getIndexes()
      dispatch(ripActions.setMainIndexes(mainIndexes))
      dispatch(ripActions.setExtraIndexes(extraIndexes))
    }
  }, [data]) 

  const handleSelectAllOnClick = (event: React.ChangeEvent, checked: boolean) => {
    if (checked) {
      data?.source.titles.forEach((value, index) => {
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
              <TableCell width="75%">Type</TableCell>
              <TableCell width="10%">Runtime</TableCell>
              <TableCell width="15%">Filename</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            { data 
              ? (
                data.source.titles.map((title, index) => {
                  let progress: number = 0
                  let buffer: number | undefined
                  let statusText: string | undefined
                  if (completedIndexes.indexOf(index) > -1) {
                    progress = 100
                  } else if (
                    index === currentIndex
                    && latestProgressValueEvent !== undefined
                    && latestCurrentProgressEvent 
                  ) {
                    statusText = latestCurrentProgressEvent.name
                    if (latestCurrentProgressEvent.name === "Saving to MKV file") {
                      progress = (latestProgressValueEvent.current / latestProgressValueEvent.max) * 100
                    } else {
                      buffer = (latestProgressValueEvent.current / latestProgressValueEvent.max) * 100
                    }
                  }
                  return (
                    <TOCRow 
                      key={index} 
                      index={index} 
                      data={title} 
                      progress={progress}
                      buffer={buffer}
                      statusText={statusText}
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

export const TOCRow = ({ index, data, progress = 0, buffer, statusText }: RowProps) => {
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

  const handleRadioButtonChange = (event: React.ChangeEvent, value: string) => {
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
      <WidgetWrapper>
        <div>
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
        </div>
        <StatusWrapper>
          <div>{statusText ?? ''}</div>
          { isSelected
            ? <LinearProgress variant={buffer !== undefined ? "buffer" : "determinate"} value={progress ?? 0} valueBuffer={buffer} />
            : <LinearProgress variant="determinate" value={0} color="secondary" />
          }
        </StatusWrapper>
      </WidgetWrapper>
    </TableCell>
    <TableCell>{data.runtime}</TableCell>
    <TableCell>{data.filename}</TableCell>
  </TableRow>
}