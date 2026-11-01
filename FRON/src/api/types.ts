/** Shared TypeScript types that mirror the FastAPI response schemas. */

export interface ApiError {
  detail: string
  error_code?: string
}

export interface PageMeta {
  page: number
  page_size: number
  total: number
  total_pages: number
}

export interface Paginated<T> {
  items: T[]
  meta: PageMeta
}

// ---- Auth ----
export interface LoginRequest {
  email: string
  password: string
}

export interface SignupRequest {
  email: string
  password: string
  full_name: string
  preferred_language?: string
}

export interface Token {
  access_token: string
  token_type: string
}

// ---- User ----
export type UserRole = 'farmer' | 'expert'

export interface User {
  id: number
  email: string
  full_name: string
  role: UserRole
  preferred_language: string
  is_active: boolean
  created_at: string
}

export interface UserUpdate {
  full_name?: string
  preferred_language?: string
  password?: string
}

// ---- Crop ----
export interface Crop {
  id: number
  name: string
  scientific_name?: string
  description?: string
  is_supported: boolean
  disease_count: number
  created_at: string
}

// ---- Disease ----
export type ReviewStatus = 'draft' | 'reviewed' | 'demonstration'

export interface DiseaseListItem {
  id: number
  name: string
  crop_id: number
  crop_name: string
  label_key?: string
  review_status: ReviewStatus
}

export interface Disease {
  id: number
  crop_id: number
  crop_name: string
  name: string
  label_key?: string
  symptoms?: string
  possible_causes?: string
  preventive_measures?: string
  recommended_next_steps?: string
  expert_consultation_guidance?: string
  advisory_source?: string
  review_status: ReviewStatus
  last_reviewed_date?: string
  is_active: boolean
  available_languages: string[]
  created_at: string
}

export interface Advisory {
  disease_id: number
  disease_name: string
  crop_name: string
  language: string
  is_translated: boolean
  review_status: ReviewStatus
  last_reviewed_date?: string
  symptoms?: string
  possible_causes?: string
  preventive_measures?: string
  recommended_next_steps?: string
  expert_consultation_guidance?: string
  advisory_source?: string
  disclaimer: string
}

// ---- Scan ----
export type PredictionStatus = 'pending' | 'completed' | 'uncertain' | 'unsupported' | 'failed'

export interface PredictionCandidate {
  label: string
  confidence: number
}

export interface ScanListItem {
  id: number
  crop_id: number
  crop_name: string
  disease_id?: number
  disease_name?: string
  prediction_status: PredictionStatus
  predicted_label?: string
  confidence?: number
  image_path: string
  created_at: string
}

export interface Scan {
  id: number
  user_id: number
  crop_id: number
  crop_name: string
  disease_id?: number
  disease_name?: string
  client_id?: string
  image_path: string
  crop_variety?: string
  field_info?: string
  prediction_status: PredictionStatus
  predicted_label?: string
  confidence?: number
  top_predictions?: PredictionCandidate[]
  model_version?: string
  is_mock_prediction: boolean
  notes?: string
  created_at: string
  updated_at: string
}

// ---- Expert Request ----
export type ExpertRequestStatus = 'pending' | 'in_review' | 'resolved' | 'closed'

export interface ExpertRequest {
  id: number
  scan_id: number
  user_id: number
  expert_id?: number
  status: ExpertRequestStatus
  question?: string
  expert_notes?: string
  consent_shared: boolean
  created_at: string
  updated_at: string
}

// ---- Feedback ----
export interface Feedback {
  id: number
  scan_id: number
  user_id: number
  is_correct?: boolean
  correct_label?: string
  comments?: string
  created_at: string
}

// ---- Health ----
export interface Health {
  status: string
  app: string
  version: string
  database: string
  prediction_mode: string
  model_loaded: boolean
}
