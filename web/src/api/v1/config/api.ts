import { endpointsV1, type ApiModel } from "@/api/endpoints"
import { api } from ".."
import type { Config } from "./types"

export const configApi = api.injectEndpoints({
  endpoints: (build) => ({
    getConfig: build.query<Config, void, ApiModel['v1']['config']>({
      providesTags: ['api/config'],
      query: () => '/config',
      transformResponse: (response) => response.data
    }),
    reloadConfig: build.mutation<Config, void, ApiModel['v1']['config']>({
      invalidatesTags: ['api/config'],
      query: () => '/config.reload',
      transformResponse: (response) => response.data,
    }),
    putConfig: build.mutation<Config, Partial<Config>, ApiModel['v1']['config']>({
      invalidatesTags: ['api/config'],
      query: (body: Partial<Config>) => ({
        url: '/config',
        method: 'PUT',
        body
      }),
      transformResponse: (response) => response.data,
    })
  }),
})

export const { useGetConfigQuery, useReloadConfigMutation, usePutConfigMutation } = configApi