import type { TmdbConfiguration } from "./v1/tmdb/store"
import type { Toc as TocV1 } from "./v1/toc/types"
import { BACKEND, type Response as ResponseV1 } from "./v1"
import type { State as StateV1 } from "./v1/state/types"
import type { TmdbSearchResultMovie, TmdbSearchResultShow } from "./v1/tmdb/types"
import type { Config } from "./v1/config/types"
import type { ApiError } from "./v1/error/types"

export const endpoints = {
  disc: {
    eject: () => `${BACKEND}/api/v1/disc/eject`,
  },
  toc: {
    get: () => `${BACKEND}/api/v1/toc`,
    stop: () => `${BACKEND}/api/v1/toc.stop`,
  },
  state: {
    get: (path?: string) => `${BACKEND}/api/v1/state${path ? "/" + path : ""}`,
    resetSocket: () => `${BACKEND}/api/v1/state.reset/socket`,
  },
  rip: {
    start: () => `${BACKEND}/api/v1/rip`,
    stop: () => `${BACKEND}/api/v1/rip.stop`
  },
  tmdb: {
    show: (query: string) => `${BACKEND}/api/v1/tmdb/show?${new URLSearchParams({q: query})}`,
    movie: (query: string) => `${BACKEND}/api/v1/tmdb/movie?${new URLSearchParams({q: query})}`,
    configuration: () => `${BACKEND}/api/v1/tmdb/configuration`
  }
}

export const endpointsV1 = {
  disc: {
    eject: () => `/disc/eject`,
  },
  toc: () => `/toc`,
  state: {
    get: (path: string | void) => `/state${path ? "/" + path : ""}`,
    resetSocket: () => `/state.reset/socket`,
  },
  rip: {
    start: () => `/rip`,
    stop: () => `/rip.stop`
  },
  tmdb: {
    show: (query: string) => `/tmdb/show?${new URLSearchParams({q: query})}`,
    movie: (query: string) => `/tmdb/movie?${new URLSearchParams({q: query})}`,
    configuration: () => `/tmdb/configuration`
  },
  config: {
    get: () => `/config`,
    put: () => (body: Partial<Config>) => ({
      url: '/api/v1/config',
      method: 'PUT',
      body
    }),
    reload: () => () => `/config.reload`
  },
  error: {
    get: () => `/error`,
    clear: () => `/error.clear`
  }
}

export type ApiModel = {
  v1: {
    'disc/eject': ResponseV1<null>;
    'state': ResponseV1<StateV1>;
    'toc': ResponseV1<TocV1>;
    'rip.stop': ResponseV1<null>;
    'tmdb/show': ResponseV1<TmdbSearchResultShow[]>;
    'tmdb/movie': ResponseV1<TmdbSearchResultMovie[]>;
    'tmdb/configuration': ResponseV1<TmdbConfiguration>;
    'config': ResponseV1<Config>;
    'config.reload': ResponseV1<Config>;
    'error': ResponseV1<ApiError>;
  }
}