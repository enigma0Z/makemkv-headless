import { type ApiModel, endpointsV1 } from "@/api/endpoints";
import type { State } from "./types";
import { api } from "..";

// Define a service using a base URL and expected endpoints
export const stateApi = api.injectEndpoints({
  endpoints: (build) => ({
    getState: build.query<State, void, ApiModel['v1']['state']>({
      providesTags: ['api/state'],
      query: () => '/state',
      transformResponse: (response) => response.data
    }),
    getStateByPath: build.query<State, string, ApiModel['v1']['state']>({
      query: () => '/state',
      transformResponse: (response) => response.data
    }),
    putState: build.mutation<State, Partial<State>, ApiModel['v1']['state']>({
      query: (state) => ({
        url: '/state',
        method: 'PUT',
        body: state
      }),
      invalidatesTags: ['api/state'],
      transformResponse: (response) => response.data
    }),
    updateState: build.mutation<Partial<State>, State, ApiModel['v1']['state']>({
      query: (state) => ({
        url: '/state',
        method: 'PUT',
        body: state
      }),
      invalidatesTags: ['api/state'],
      transformResponse: (response) => response.data
    })
  }),
})

export const { useGetStateQuery, useGetStateByPathQuery } = stateApi