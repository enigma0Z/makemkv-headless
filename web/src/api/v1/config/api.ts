import { api } from "@/api"
import { endpointsV1, type ApiModel } from "@/api/endpoints"
import type { Config } from "./types"

const configApi = api.injectEndpoints({
  endpoints: (build) => ({
    getConfig: build.query<Config, void, ApiModel['v1']['config']>({
      query: () => endpointsV1.config.get(),
      transformResponse: (response) => response.data
    }),
    putConfig: build.query<Config, void, ApiModel['v1']['config']>({
      query: () => endpointsV1.config.get(),
      transformResponse: (response) => response.data
    }),
    reloadConfig: build.query<Config, void, ApiModel['v1']['config.reload']>({
      query: () => endpointsV1.config.reload(),
      transformResponse: (response) => response.data
    })
  }),
})

export const { useGetConfigQuery, useReloadConfigQuery } = configApi