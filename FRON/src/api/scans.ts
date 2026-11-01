import { api } from './client'
import type { Advisory, Paginated, Scan, ScanListItem } from './types'

export const scansApi = {
  /**
   * Create a new scan — multipart/form-data (image + crop_id).
   * Uses the real backend prediction pipeline; never fabricates results.
   */
  create: (cropId: number, imageFile: File, extras?: {
    cropVariety?: string
    fieldInfo?: string
    notes?: string
    clientId?: string
  }) => {
    const form = new FormData()
    form.append('crop_id', String(cropId))
    form.append('image', imageFile)
    if (extras?.cropVariety) form.append('crop_variety', extras.cropVariety)
    if (extras?.fieldInfo)   form.append('field_info',   extras.fieldInfo)
    if (extras?.notes)       form.append('notes',        extras.notes)
    if (extras?.clientId)    form.append('client_id',    extras.clientId)
    return api
      .post<Scan>('/api/scans', form, {
        headers: { 'Content-Type': 'multipart/form-data' },
      })
      .then((r) => r.data)
  },

  list: (page = 1, pageSize = 20) =>
    api
      .get<Paginated<ScanListItem>>('/api/scans', { params: { page, page_size: pageSize } })
      .then((r) => r.data),

  get: (scanId: number) =>
    api.get<Scan>(`/api/scans/${scanId}`).then((r) => r.data),

  delete: (scanId: number) =>
    api.delete(`/api/scans/${scanId}`).then((r) => r.data),

  getAdvisory: (diseaseId: number, lang = 'en') =>
    api
      .get<Advisory>(`/api/advisories/${diseaseId}`, { params: { lang } })
      .then((r) => r.data),

  submitFeedback: (scanId: number, isCorrect: boolean, comments?: string) =>
    api
      .post('/api/feedback', { scan_id: scanId, is_correct: isCorrect, comments })
      .then((r) => r.data),

  submitExpertRequest: (scanId: number, question: string, consentShared: boolean) =>
    api
      .post('/api/expert-requests', { scan_id: scanId, question, consent_shared: consentShared })
      .then((r) => r.data),
}
