import type { TmdbConfiguration } from "./store/tmdb"
import type { Toc as TocV1 } from "./store/toc"
import type { Response as ResponseV1 } from "./v1"
import type { State as StateV1 } from "./v1/types/State"
import type { TmdbSearchResultMovie, TmdbSearchResultShow } from "./v1/types/Tmdb"

type Endpoint = (params?: any) => string

export const BACKEND = `${window.location.protocol}//${window.location.hostname}:4000`
// export const BACKEND = "http://localhost:4000"

export const endpoints = {
  disc: {
    eject: () => `${BACKEND}/api/v1/disc/eject`,
  },
  toc: () => `${BACKEND}/api/v1/toc`,
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

export type ApiModel = {
  v1: {
    'disc/eject': ResponseV1<null>;
    'state': ResponseV1<StateV1>;
    'toc': ResponseV1<TocV1>;
    'rip.stop': ResponseV1<null>;
    'tmdb/show': ResponseV1<TmdbSearchResultShow[]>;
    'tmdb/movie': ResponseV1<TmdbSearchResultMovie[]>;
    'tmdb/configuration': ResponseV1<TmdbConfiguration>;
  }
}