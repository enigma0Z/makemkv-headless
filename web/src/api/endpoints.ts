type Endpoint = (params?: any) => string
type EndpointsMap = { [index: string]: Endpoint }

export const BACKEND = "http://localhost:4000"

const endpoints: EndpointsMap = {
  toc: () => `${BACKEND}/api/v1/toc`,
  state: () => `${BACKEND}/api/v1/state`,
  rip: () => `${BACKEND}/api/v1/rip`,
  tmdb_show: (query: string) => `${BACKEND}/api/v1/tmdb/show?${new URLSearchParams({q: query})}`,
  tmdb_movie: (query: string) => `${BACKEND}/api/v1/tmdb/movie?${new URLSearchParams({q: query})}`
}

export default endpoints