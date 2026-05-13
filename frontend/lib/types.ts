import type { components } from "./openapi"

// Base types from openapi schema
export type SessionCreated = components["schemas"]["SessionCreated"]
export type ResponseItem = components["schemas"]["ResponseItem"]
export type SubmitResponsesRequest = components["schemas"]["SubmitResponsesRequest"]
export type RiasecScores = components["schemas"]["RiasecScoresOut"]
export type RiasecDimension = "R" | "I" | "A" | "S" | "E" | "C"

// MajorSummary extended with description field (added in v2 API)
export type MajorSummary = components["schemas"]["MajorSummary"] & {
  description?: string | null
}

export interface SubMajorItem {
  code: string
  name: string
}

// RecommendationItem extended with interest scoring fields
export type RecommendationItem = Omit<components["schemas"]["RecommendationItem"], "major"> & {
  major: MajorSummary
  interest_score?: number | null
  combined_score?: number | null
  is_conflict?: boolean | null
  sub_majors?: SubMajorItem[]
}

// AssessmentResult extended with interest_scores
export type AssessmentResult = Omit<
  components["schemas"]["AssessmentResult"],
  "recommendations"
> & {
  recommendations: RecommendationItem[]
  interest_scores?: Record<string, number> | null
  ai_interpretation?: string | null
}

// Interest selection types (not in openapi yet)
export interface SampleMajorCategory {
  code: string
  name: string
  description: string
  typical_representatives: string
}

export interface InterestOption {
  category_code: string
  category_name: string
  sample: SampleMajorCategory
}

export interface InterestRoundResponse {
  round_number: number
  options: InterestOption[]
}

export interface InterestSubmitRequest {
  round_number: number
  selected_category_code: string
  presented_category_codes: string[]
  presented_sample_codes: string[]
}

export interface InterestSubmitResponse {
  should_stop: boolean
  next_round: InterestRoundResponse | null
}
