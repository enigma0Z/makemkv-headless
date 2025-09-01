import { type ApiModel, endpointsV1 } from "@/api/endpoints";
import type { State } from "./types";
import { api } from "@/api";

// Define a service using a base URL and expected endpoints
const stateApi = api.injectEndpoints({
  endpoints: (build) => ({
    getState: build.query<State, void, ApiModel['v1']['state']>({
      query: () => endpointsV1.state.get(),
      transformResponse: (response) => response.data
    }),
    getStateByPath: build.query<State, string, ApiModel['v1']['state']>({
      query: (path: string) => endpointsV1.state.get(path),
      transformResponse: (response) => response.data
    }),
  }),
})

export const { useGetStateQuery, useGetStateByPathQuery } = stateApi