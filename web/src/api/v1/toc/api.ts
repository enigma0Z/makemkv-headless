import { type ApiModel, endpointsV1 } from "@/api/endpoints";
import { api } from "@/api";
import type { Toc } from "./types";

// Define a service using a base URL and expected endpoints
const tocApi = api.injectEndpoints({
  endpoints: (build) => ({
    getToc: build.query<Toc, void, ApiModel['v1']['toc']>({
      query: () => endpointsV1.state.get(),
      transformResponse: (response) => response.data
    })
  }),
})

export const { useGetTocQuery } = tocApi