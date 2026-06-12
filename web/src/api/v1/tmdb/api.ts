import { type ApiModel } from "@/api/endpoints"
import { api } from ".."
import type { TmdbConfiguration, TmdbSearchResultMovie, TmdbSearchResultShow } from "./types"

const tmdbApi = api.injectEndpoints({
  endpoints: (build) => ({
    getTmdbConfiguration: build.query<TmdbConfiguration, void, ApiModel['v1']['tmdb/configuration']>({
      providesTags: [{ type: 'api/tmdb/configuration' }],
      query: () => '/tmdb/configuration',
      transformResponse: (response) => response.data
    }),
    getTmdbSearch: build.query<TmdbSearchResultShow[] | TmdbSearchResultMovie[], {content: string, query: string}, ApiModel['v1']['tmdb/show']>({
      query: ({content, query}) => `/tmdb/${content.toLowerCase()}?${new URLSearchParams({q: query})}`,
      transformResponse: (response) => response.data ?? []
    }),
  }),
})

export const { useGetTmdbConfigurationQuery, useGetTmdbSearchQuery } = tmdbApi