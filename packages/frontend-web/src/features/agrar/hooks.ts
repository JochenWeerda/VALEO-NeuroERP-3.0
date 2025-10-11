import { type UseMutationResult, type UseQueryResult, useMutation, useQuery } from '@tanstack/react-query'
import { mutationKeys, queryKeys } from '@/lib/query'
import {
  fetchFertilizerProductById,
  fetchFertilizerProducts,
  fetchSeedProductById,
  fetchSeedProducts,
  submitSeedOrder,
} from './api'
import { type FertilizerProduct, type SeedOrderPayload, type SeedProduct } from './types'

export const useSeedProducts = (): UseQueryResult<SeedProduct[]> =>
  useQuery<SeedProduct[]>({
    queryKey: queryKeys.agrar.seeds.list(),
    queryFn: fetchSeedProducts,
  })

export const useSeedProduct = (productId: string): UseQueryResult<SeedProduct | undefined> =>
  useQuery<SeedProduct | undefined>({
    queryKey: queryKeys.agrar.seeds.detail(productId),
    queryFn: () => fetchSeedProductById(productId),
    enabled: productId.length > 0,
  })

export const useFertilizerProducts = (): UseQueryResult<FertilizerProduct[]> =>
  useQuery<FertilizerProduct[]>({
    queryKey: queryKeys.agrar.fertilizers.list(),
    queryFn: fetchFertilizerProducts,
  })

export const useFertilizerProduct = (productId: string): UseQueryResult<FertilizerProduct | undefined> =>
  useQuery<FertilizerProduct | undefined>({
    queryKey: queryKeys.agrar.fertilizers.detail(productId),
    queryFn: () => fetchFertilizerProductById(productId),
    enabled: productId.length > 0,
  })

export const useSubmitSeedOrder = (): UseMutationResult<{ orderId: string }, Error, SeedOrderPayload> =>
  useMutation<{ orderId: string }, Error, SeedOrderPayload>({
    mutationKey: mutationKeys.agrar.seedOrders.create,
    mutationFn: submitSeedOrder,
  })
