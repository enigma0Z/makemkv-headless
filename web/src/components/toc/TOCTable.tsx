import { useAppDispatch, useAppSelector } from "@/api/store"
import { ripActions } from "@/api/store/rip"
import type { TitleInfo, Toc } from "@/api/types/Toc"
import { hmsToSeconds } from "@/util/string"
import { Button, Card, Checkbox, FormControlLabel, Radio, RadioGroup, Table, TableCell, TableContainer, TableHead, TableRow } from "@mui/material"
import { useEffect, useState } from "react"

type TableProps = {
  content?: "show" | "movie"
}

type TitleGroup = {
  title: TitleInfo,
  index: number,
  matches: number[]
}

const EPISODE_LENGTH_TOLERANCE_SECONDS = 120

export const TOCTable = () => {
  const dispatch = useAppDispatch()

  const mainIndexes = useAppSelector((state) => state.rip.sort_info.main_indexes)
  const extraIndexes = useAppSelector((state) => state.rip.sort_info.extra_indexes)
  const content = useAppSelector((state) => state.rip.destination.content)

  const [tocData, setTocData] = useState<Toc>()
  const [tocLoading, setTocLoading] = useState<boolean>(false)
  const [oldMainIndexes, setOldMainIndexes] = useState<number[]>([])
  const [oldExtraIndexes, setOldExtraIndexes] = useState<number[]>([])

  const getLongestTitle = () => {
    let longestTitleIndex = 0
    let longestTitleLength = 0
    tocData?.source.titles.forEach((title, index) => {
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

    tocData?.source.titles.forEach((outerTitle, outerIndex) => {
      const newTitleGroup: TitleGroup = { title: outerTitle, index: outerIndex, matches: [] }
      const outerTitleLength = hmsToSeconds(outerTitle.runtime)
      tocData.source.titles.forEach((innerTitle, innerIndex) => {
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
    for (let i=0; i < (tocData?.source.titles.length ?? 0); i++) {
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
    for (let i=0; i < (tocData?.source.titles.length ?? 0); i++) {
      if (longestTitleGroup.matches.indexOf(i) > -1) {
        mainIndexes.push(i)
      } else {
        extraIndexes.push(i)
      }
    }
    return {mainIndexes, extraIndexes}
  }

  const handleLoadTocClick = () => {
    console.info('Fetching TOC')
    fetch("http://localhost:5000/api/v1/toc", { method: 'GET' })
      .then(response => response.json())
      .then(json => {
        console.log('response json', json)
        setTocData(json)
      })
  }

  useEffect(() => {
    if (tocData) {
      dispatch(ripActions.setTocLength(tocData.source.titles.length))

      let longestTitleIndex = 0
      let longestTitleLength = 0
      tocData.source.titles.forEach((title, index) => {
        const outerTitleLength = hmsToSeconds(title.runtime)
        if (outerTitleLength > longestTitleLength) {
          longestTitleLength = outerTitleLength
          longestTitleIndex = index
        }
      })

      console.debug('longestTitleIndex', longestTitleIndex)
      console.debug('longestTitleLength', longestTitleLength)

      let getIndexes: () => { mainIndexes: number[], extraIndexes: number[] }
      if (content === "movie") getIndexes = getMovieIndexes
      else getIndexes = getShowIndexes

      const {mainIndexes, extraIndexes} = getIndexes()
      dispatch(ripActions.setMainIndexes(mainIndexes))
      dispatch(ripActions.setExtraIndexes(extraIndexes))
    }
  }, [tocData]) 

  const handleSelectAllOnClick = (event: React.ChangeEvent, checked: boolean) => {
    if (checked) {
      tocData?.source.titles.forEach((value, index) => {
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
    <Button onClick={handleLoadTocClick}>Load TOC</Button>
    <Card>
      <TableContainer>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell sx={{width: "1px"}}><Checkbox 
                onChange={handleSelectAllOnClick}
              /></TableCell>
              <TableCell sx={{width: "1px"}}>#</TableCell>
              <TableCell>Type</TableCell>
              <TableCell>Runtime</TableCell>
              <TableCell>Filename</TableCell>
            </TableRow>
          </TableHead>
          { tocData 
            ? tocData.source.titles.map((title, index) => <TOCRow key={index} index={index} data={title} />)
            : <TableRow>
                <TableCell colSpan={4}>No data</TableCell>
              </TableRow>
          }
        </Table>
      </TableContainer>
    </Card>
  </>)
}

type RowProps = {
  index: number;
  data: TitleInfo;
}

export const TOCRow = ({ index, data }: RowProps) => {
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
    <TableCell><Checkbox 
      checked={isSelected}
      onChange={handleCheckboxOnChange}
    /></TableCell>
    <TableCell>{index}</TableCell>
    <TableCell>
      <RadioGroup
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
      >
        <FormControlLabel disabled={!isSelected} value="main" control={<Radio />} label="Main" />
        <FormControlLabel disabled={!isSelected} value="extra" control={<Radio />} label="Extra" />
      </RadioGroup>
    </TableCell>
    <TableCell>{data.runtime}</TableCell>
    <TableCell>{data.filename}</TableCell>
  </TableRow>
}