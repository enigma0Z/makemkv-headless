import { ConfigTextField } from "@/components/fields/config/ConfigTextField"
import { Link } from "@mui/material"

export const TmdbTab = () => {

  return <>
    <ConfigTextField 
      configItem="tmdb_token"
      label="TMDB API Token"
    />
    <Link href="https://developer.themoviedb.org/docs/getting-started" target="_blank">
      Get an API key
    </Link>
  </>
}