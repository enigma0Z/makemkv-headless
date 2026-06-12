import { type ApiModel } from "@/api/endpoints";
import { api } from "..";
import {type Response as ResponseV1 } from ".."

// Define a service using a base URL and expected endpoints
export const tocApi = api.injectEndpoints({
  endpoints: (build) => ({
    getToc: build.query<ApiModel['v1']['toc'], void, ApiModel['v1']['toc']>({
      providesTags: ['api/toc'],
      query: () => '/toc',
    }),
    startTocLoad: build.mutation<void, void, ResponseV1<any>>({
      invalidatesTags: ['api/toc'],
      query: () => '/toc.start',
      transformResponse: (response) => response.data
    }),
    stopTocLoad: build.mutation<void, void, ResponseV1<any>>({
      invalidatesTags: ['api/toc'],
      query: () => '/toc.stop',
      transformResponse: (response) => response.data
    })
  }),
})

export const { useGetTocQuery, useStartTocLoadMutation, useStopTocLoadMutation } = tocApi