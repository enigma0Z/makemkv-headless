export type TmdbConfiguration = {
  change_keys?: string[];
  images?: {
    base_url: string;
    secure_base_url: string;
    backdrop_sizes: string[];
    logo_sizes: string[];
    poster_sizes: string[];
    profile_sizes: string[];
    still_sizes: string[];
  }
}

export type TmdbState = {
  configuration?: TmdbConfiguration
}

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