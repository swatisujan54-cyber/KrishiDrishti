import { api } from './client'
import type { Crop, Paginated } from './types'

export const cropsApi = {
  list: (page = 1, pageSize = 50) =>
    api
      .get<Paginated<Crop>>('/api/crops', { params: { page, page_size: pageSize } })
      .then((r) => r.data),

  get: (cropId: number) =>
    api.get<Crop>(`/api/crops/${cropId}`).then((r) => r.data),
}
