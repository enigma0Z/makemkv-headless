type Endpoint = (params?: any) => string

export const BACKEND = "http://localhost:4000"

const endpoints: { [index: string]: Endpoint } = {
  toc: () => `${BACKEND}/api/v1/toc`,
  status: () => `${BACKEND}/api/v1/status`,
  rip: () => `${BACKEND}/api/v1/rip`
}

export default endpoints