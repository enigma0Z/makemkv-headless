import { createApi, fetchBaseQuery } from "@reduxjs/toolkit/query/react";

let backend_port = window.location.port;

if (import.meta.env.DEV) {
  backend_port = import.meta.env.BACKEND_PORT ?? 4000
  console.info(`Setting backend port to ${backend_port}`)
}

export const BACKEND_HOST_PORT = `${window.location.hostname}:${backend_port}`
export const BACKEND = `${window.location.protocol}//${BACKEND_HOST_PORT}`

export type Response<T> = {
  status: (
    'success' |
    'failure' |
    'started' |
    'in progress' |
    'done' |
    'stopped' |
    'error'
  ),
  data: T
}

export const api = createApi({
  tagTypes: ['error', 'api/config', 'api/state', 'api/toc'],
  baseQuery: fetchBaseQuery({ baseUrl: `${BACKEND}/api/v1` }),
  endpoints: () => ({}),
})