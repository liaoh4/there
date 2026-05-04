/**
 * 从自动生成的 openapi 类型中提取常用类型，方便组件直接使用。
 * 如果后端 schema 改了，重新运行 npx openapi-typescript 更新底层文件，
 * 再同步修改这里的别名即可。
 */

import type { components } from "./openapi"

export type SessionCreated = components["schemas"]["SessionCreated"]
export type ResponseItem = components["schemas"]["ResponseItem"]
export type SubmitResponsesRequest = components["schemas"]["SubmitResponsesRequest"]
export type RiasecScores = components["schemas"]["RiasecScoresOut"]
export type MajorSummary = components["schemas"]["MajorSummary"]
export type RecommendationItem = components["schemas"]["RecommendationItem"]
export type AssessmentResult = components["schemas"]["AssessmentResult"]

export type RiasecDimension = "R" | "I" | "A" | "S" | "E" | "C"
