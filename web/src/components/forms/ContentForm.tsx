import { useAppSelector } from "@/api/store"
import { ripActions } from "@/api/store/rip"
import { FormControl, FormGroup, InputLabel, MenuItem, Select, TextField } from "@mui/material"
import { useDispatch } from "react-redux"

export const CombinedShowMovieForm = () => {
  // const [library, setLibrary] = useState<string>()
  // const [media, setMedia] = useState<string>()
  // const [content, setContent] = useState<string>()

  const library = useAppSelector((state) => state.rip.destination?.library)
  const media = useAppSelector((state) => state.rip.destination?.media)
  const content = useAppSelector((state) => state.rip.destination?.content)
  const seasonNumber = useAppSelector((state) => state.rip.sort_info.season_number)
  const firstEpisode = useAppSelector((state) => state.rip.sort_info.first_episode)
  const dispatch = useDispatch();

  return <>
    <FormGroup sx={{
      display: "flex",
      flexDirection: "row",
      gap: "10px",
      flexGrow: 1,
      div: {
        flex: 1
      }
    }}>
      <FormControl>
        <InputLabel id="select-library-label">Library</InputLabel>
        <Select
          labelId="select-library-label"
          id="select-library"
          value={library}
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
          value={media}
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
          value={content}
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
      <FormControl
        disabled={ content !== "show" }
      >
        <TextField 
          disabled={ content !== "show" }
          label="Season Number"
          type="number"
          value={seasonNumber}
          onChange={({target: {value}}) => {
            console.log(value)
            if (value.match(/^\d*$/)) {
              console.log("matches")
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
    </FormGroup>
  </>
}