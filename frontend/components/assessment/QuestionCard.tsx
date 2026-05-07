"use client"

import type { Question } from "@/lib/questions"
import Button from "@/components/ui/Button"

const OPTIONS = [
  { value: 1, label: "完全不符合" },
  { value: 2, label: "比较不符合" },
  { value: 3, label: "不确定" },
  { value: 4, label: "比较符合" },
  { value: 5, label: "完全符合" },
]

interface QuestionCardProps {
  question: Question
  index: number
  total: number
  onAnswer: (value: number) => void
}

export default function QuestionCard({
  question,
  index,
  total,
  onAnswer,
}: QuestionCardProps) {
  return (
    <div className="w-full max-w-lg mx-auto">
      <p className="text-sm text-gray-400 mb-2 text-center">
        {index + 1} / {total}
      </p>
      <h2 className="text-xl font-semibold text-gray-800 text-center mb-8 leading-relaxed">
        {question.text}
      </h2>
      <div className="flex flex-col gap-3">
        {OPTIONS.map((opt) => (
          <Button
            key={opt.value}
            variant="outline"
            className="w-full text-left justify-start"
            onClick={() => onAnswer(opt.value)}
          >
            {opt.label}
          </Button>
        ))}
      </div>
    </div>
  )
}
