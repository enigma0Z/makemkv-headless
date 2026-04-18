import { api } from "@/api"
import { endpointsV1, type ApiModel } from "@/api/endpoints"
import type { Config } from "./types"

const configApi = api.injectEndpoints({
  endpoints: (build) => ({
    getConfig: build.query<Config, void, ApiModel['v1']['config']>({
      providesTags: ['config'],
      query: () => endpointsV1.config.get(),
      transformResponse: (response) => response.data
    }),
    reloadConfig: build.mutation<Config, void, ApiModel['v1']['config']>({
      invalidatesTags: ['config'],
      query: endpointsV1.config.reload(),
      transformResponse: (response) => response.data,
    }),
    putConfig: build.mutation<Config, Partial<Config>, ApiModel['v1']['config']>({
      invalidatesTags: ['config'],
      query: endpointsV1.config.put(),
      transformResponse: (response) => response.data,
    })
  }),
})

export const { useGetConfigQuery, useReloadConfigMutation, usePutConfigMutation } = configApi