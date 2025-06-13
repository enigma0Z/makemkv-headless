import { useAppSelector } from "@/api/store"
import { ripActions } from "@/api/store/rip"
import { Autocomplete, Card, InputLabel, MenuItem, Select, TextField } from "@mui/material"
import { useDispatch } from "react-redux"
import { ContentFormControl, FirstEpisodeFormControl, LibraryFormControl, MediaFormControl, NameIdFormControl, SeasonFormControl, StyledFormGroup } from "./ContentForm.styles"
import React, { useState } from "react"
import { throttle } from "lodash"
import endpoints from "@/api/endpoints"
import type { TmdbSearchResult } from "@/api/types/tmdb"
import { AutocompleteWrapper } from "@/theme"

export const CombinedShowMovieForm = ({ onError, onClearError }: BaseProps) => {
  const dispatch = useDispatch();

  const name = useAppSelector((state) => state.rip.sort_info.name)
  const id = useAppSelector((state) => state.rip.sort_info.id)
  const library = useAppSelector((state) => state.rip.destination?.library)
  const media = useAppSelector((state) => state.rip.destination?.media)
  const content = useAppSelector((state) => state.rip.destination?.content)
  const seasonNumber = useAppSelector((state) => state.rip.sort_info.season_number)
  const firstEpisode = useAppSelector((state) => state.rip.sort_info.first_episode)

  const [ nameValue, setNameValue ] = useState<TmdbSearchResult>()
  const [ nameOptions, setNameOptions ] = useState<(TmdbSearchResult)[]>()

  const getOptionLabel = (option: TmdbSearchResult) => 
    option ? `${option.name ?? option.title} / ${option.first_air_date ?? option.release_date} (tmdbid-${option.id})` : ""
  
  const updateOptions = throttle((searchText: string) => {
    console.log('updateOptions', searchText)
    const foundOption = nameOptions?.find((option) => (
      option.label === searchText
    ))
    if (!foundOption && searchText !== '') {
      if (content?.toLowerCase() === 'show') {
        fetch(endpoints.tmdb_show(searchText), { method: 'GET' })
        .then(response => response.json())
        .then(json => {
          json.forEach((option: TmdbSearchResult) => {
            option.label = getOptionLabel(option)
          })
          setNameOptions(json)
        })
      } else if (content?.toLowerCase() === 'movie') {
        fetch(endpoints.tmdb_movie(searchText), { method: 'GET' })
        .then(response => response.json())
        .then(json => {
          json.forEach((option: TmdbSearchResult) => {
            option.label = getOptionLabel(option)
          })
          setNameOptions(json)
        })
      }
    }
  }, 2000, {leading: false, trailing: true})

  const handleNameOnInputChange = (_event: React.SyntheticEvent, value: string) => {
    console.debug('handleNameOnInputChange', value)
    setNameValue({ label: value })
    updateOptions(value)
  }

  const handleNameOnChange = (_event: React.SyntheticEvent, value: TmdbSearchResult | null) => {
    console.log('handleNameChange', value)
    if (value?.name) dispatch(ripActions.setName(value.name));
    else if (value?.title) dispatch(ripActions.setName(value.title));
    value?.id && dispatch(ripActions.setId(`${value.id}`))
  }

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
        <LibraryFormControl>
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
        </LibraryFormControl>

        <MediaFormControl>
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
        </MediaFormControl>

        <ContentFormControl>
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
        </ContentFormControl>
        <NameIdFormControl
          disabled={content === ""}
        >
          <AutocompleteWrapper>
            <Autocomplete
              disabled={content === "" || content === undefined || content === null}
              renderInput={(params) => ( <TextField {...params} label="Name" />)} 
              onInputChange={handleNameOnInputChange}
              onChange={handleNameOnChange}
              options={nameOptions ?? []}
              getOptionLabel={(option) => option.label ?? ''}
              filterOptions={(options, state) => {
                const filteredOptions = options.filter((option) => {
                  state.getOptionLabel(option).startsWith(state.inputValue)
                })
                return filteredOptions.length > 0 ? filteredOptions : options
              }}
              renderOption={({key, ...props}, option: TmdbSearchResult, _state, ownerState) => {
                return (
                  <li 
                    key={key} 
                    {...props}
                  >
                    <Card
                      elevation={12}
                      sx={{
                        padding: "10px",
                        width: "100%",
                      }}
                    >
                      <div>{ownerState.getOptionLabel(option)}</div>
                      <div>{option.overview}</div>
                    </Card>
                  </li>
                )
              }}
              value={nameValue ?? { label: `${name} - ${id}` } }
              fullWidth
              freeSolo
            />
          </AutocompleteWrapper>
        </NameIdFormControl>
        <SeasonFormControl
          disabled={ content !== "show" }
        >
          <TextField 
            disabled={ content !== "show" }
            label="Season #"
            type="number"
            value={seasonNumber ?? ""}
            onChange={({target: {value}}) => {
              if (value.match(/^\d*$/)) {
                dispatch(ripActions.setSeasonNumber(parseInt(value)))
              }
            }}
          />
        </SeasonFormControl>
        <FirstEpisodeFormControl
          disabled={ content !== "show" }
        >
          <TextField 
            disabled={ content !== "show" }
            label="First Ep #"
            type="number"
            value={firstEpisode ?? ""}
            onChange={({target: {value}}) => {
              console.log(value)
              if (value.match(/^\d*$/)) {
                dispatch(ripActions.setFirstEpisode(parseInt(value)))
              }
            }}
          />
        </FirstEpisodeFormControl>
    </StyledFormGroup>
  </>
}