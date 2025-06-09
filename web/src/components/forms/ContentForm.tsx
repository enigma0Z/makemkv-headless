import { useAppSelector } from "@/api/store"
import { ripActions } from "@/api/store/rip"
import { FormControl, InputLabel, MenuItem, Select, TextField } from "@mui/material"
import { useDispatch } from "react-redux"
import { StyledFormGroup } from "./ContentForm.styles"

export const CombinedShowMovieForm = ({ onError, onClearError }: BaseProps) => {
  const dispatch = useDispatch();

  const name = useAppSelector((state) => state.rip.sort_info.name)
  const id = useAppSelector((state) => state.rip.sort_info.id)
  const library = useAppSelector((state) => state.rip.destination?.library)
  const media = useAppSelector((state) => state.rip.destination?.media)
  const content = useAppSelector((state) => state.rip.destination?.content)
  const seasonNumber = useAppSelector((state) => state.rip.sort_info.season_number)
  const firstEpisode = useAppSelector((state) => state.rip.sort_info.first_episode)

  const isValid = (
    ( name !== null && name !== undefined ) &&
    ( id !== null && id !== undefined ) &&
    ( library === "kids" || library === "main" ) &&
    ( media === "dvd" || media === "blu-ray" ) && 
    ( content === "show" && (
        seasonNumber !== null && seasonNumber !== undefined &&
        firstEpisode !== null && firstEpisode !==  undefined ) || 
      content === "movie" )
  )

  if (isValid) onClearError && onClearError();
  else onError && onError();

  return <>
    <StyledFormGroup>
      <div>
        <FormControl>
          <InputLabel id="select-library-label">Library</InputLabel>
          <Select
            labelId="select-library-label"
            id="select-library"
            value={library ?? ''}
            label="Format"
            onChange={({ target: { value }}) => { 
              dispatch(ripActions.setLibrary(value))
            }}
            fullWidth
          >
            <MenuItem value={"main"}>Main</MenuItem>
            <MenuItem value={"kids"}>Kids</MenuItem>
          </Select>
        </FormControl>

        <FormControl>
          <InputLabel id="select-media-label">Format</InputLabel>
          <Select
            labelId="select-media-label"
            id="select-media"
            value={media ?? ''}
            label="Format"
            onChange={({ target: { value }}) => { 
              dispatch(ripActions.setMedia(value))
            }}
            fullWidth
          >
            <MenuItem value={"dvd"}>DVD</MenuItem>
            <MenuItem value={"blu-ray"}>Blu-Ray</MenuItem>
          </Select>
        </FormControl>
        <FormControl>
          <InputLabel id="select-content-label">Content</InputLabel>
          <Select
            labelId="select-content-label"
            id="select-content"
            value={content ?? ''}
            label="Format"
            onChange={({ target: { value }}) => { 
              dispatch(ripActions.setContent(value))
            }}
            fullWidth
          >
            <MenuItem value={"show"}>Show</MenuItem>
            <MenuItem value={"movie"}>Movie</MenuItem>
          </Select>
        </FormControl>
        </div><div>
        <FormControl>
          <TextField 
            label="Name"
            value={name}
            onChange={({target: {value}}) => {
              dispatch(ripActions.setName(value))
            }}
            onBlur={() => {
              // API call to search tmdb and fill out autocomplete
            }}
          />
        </FormControl>
        <FormControl>
          <TextField // Autocomplete based on name value
            label="TMDB ID"
            value={id}
            onChange={({target: {value}}) => {
              dispatch(ripActions.setId(value))
            }}
          />
        </FormControl>
        <FormControl
          disabled={ content !== "show" }
        >
          <TextField 
            disabled={ content !== "show" }
            label="Season Number"
            type="number"
            value={seasonNumber}
            onChange={({target: {value}}) => {
              if (value.match(/^\d*$/)) {
                dispatch(ripActions.setSeasonNumber(parseInt(value)))
              }
            }}
          />
        </FormControl>
        <FormControl
          disabled={ content !== "show" }
        >
          <TextField 
            disabled={ content !== "show" }
            label="First Episode"
            type="number"
            value={firstEpisode}
            onChange={({target: {value}}) => {
              console.log(value)
              if (value.match(/^\d*$/)) {
                dispatch(ripActions.setFirstEpisode(parseInt(value)))
              }
            }}
          />
        </FormControl>
      </div>
    </StyledFormGroup>
  </>
}