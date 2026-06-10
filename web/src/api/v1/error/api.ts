import { type ApiModel, endpointsV1 } from "@/api/endpoints";
import type { ApiError } from "./types";
import { api } from "..";

// Define a service using a base URL and expected endpoints
const errorApi = api.injectEndpoints({
  endpoints: (build) => ({
    getError: build.query<ApiError, void, ApiModel['v1']['error']>({
      providesTags: ['error'],
      query: () => endpointsV1.error.get(),
      transformResponse: (response) => response.data,
    }),
    clearError: build.mutation<ApiError, void, ApiModel['v1']['error']>({
      invalidatesTags: ['error'],
      query: () => endpointsV1.error.clear(),
      transformResponse: (response) => response.data,
    })
  }),
})

export const { useGetErrorQuery, useClearErrorMutation, util: errorApiUtil } = errorApi