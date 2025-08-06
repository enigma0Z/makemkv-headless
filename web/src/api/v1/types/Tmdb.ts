export type TmdbSearchResultCommon = {
  adult: boolean;
  backdrop_path: string;
  genre_ids: number[];
  id: number;
  original_language: string;
  overview: string;
  popularity: number;
  poster_path: string;
  vote_average: number;
  vote_count: number;
  label: string;
}

export type TmdbSearchResultShow = TmdbSearchResultCommon & {
  origin_country: string[];
  original_name: string;
  name: string;
  first_air_date: string;
}

export type TmdbSearchResultMovie = TmdbSearchResultCommon & {
  original_title: string;
  title: string;
  release_date: string;
  video: boolean;
}

export type TmdbSearchResult = Partial<TmdbSearchResultMovie & TmdbSearchResultShow>