import { useMutation } from "@tanstack/react-query";
import { searchNearest, attributePredict } from "@/api/predictApi";
import type {
  SearchNearestRequest,
  AttributeRequest,
  NearestTextsResponse,
  VotesResponse,
} from "@/types/prediction";
import type { AxiosError } from "axios";

export function useNearestKMutation() {
  return useMutation<NearestTextsResponse, AxiosError, SearchNearestRequest>({
    mutationFn: searchNearest,
  });
}

export function useAttributeMutation() {
  return useMutation<VotesResponse, AxiosError, AttributeRequest>({
    mutationFn: attributePredict,
  });
}
