"use client"

import {
  PolarAngleAxis,
  PolarGrid,
  Radar,
  RadarChart,
  ResponsiveContainer,
} from "recharts"

import { DIMENSIONS } from "@/lib/riasec"
import type { RiasecScores } from "@/lib/types"

interface RiasecRadarProps {
  scores: RiasecScores
}

export default function RiasecRadar({ scores }: RiasecRadarProps) {
  const data = DIMENSIONS.map((d) => ({
    dimension: d.name,
    score: scores[d.key],
  }))

  return (
    <ResponsiveContainer width="100%" height={300}>
      <RadarChart data={data}>
        <PolarGrid />
        <PolarAngleAxis
          dataKey="dimension"
          tick={{ fontSize: 13, fill: "#6b7280" }}
        />
        <Radar
          dataKey="score"
          stroke="#4f46e5"
          fill="#4f46e5"
          fillOpacity={0.2}
        />
      </RadarChart>
    </ResponsiveContainer>
  )
}
