type Endpoint = (params?: any) => string
type EndpointsMap = { [index: string]: Endpoint }

export const BACKEND = `${window.location.protocol}//${window.location.hostname}:4000`
// export const BACKEND = "http://localhost:4000"

const endpoints = {
  eject: () => `${BACKEND}/api/v1/disc/eject`,
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

export default endpoints