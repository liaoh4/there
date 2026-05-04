"use client"

import { useCallback, useEffect, useRef, useState } from "react"

import { completeSession, createSession, submitResponses } from "@/lib/api"
import { QUESTIONS } from "@/lib/questions"
import type { AssessmentResult } from "@/lib/types"

type Answers = Record<string, number>  // { "r1": 4, "i1": 5, ... }

type Phase = "loading" | "answering" | "submitting" | "done" | "error"

export function useAssessment() {
  const [sessionId, setSessionId] = useState<string | null>(null)
  const [currentIndex, setCurrentIndex] = useState(0)
  const [answers, setAnswers] = useState<Answers>({})
  const [phase, setPhase] = useState<Phase>("loading")
  const [result, setResult] = useState<AssessmentResult | null>(null)
  const [errorMsg, setErrorMsg] = useState<string | null>(null)

  const creatingRef = useRef(false)

  // 组件加载时自动创建 session
  useEffect(() => {
    if (creatingRef.current) return
    creatingRef.current = true

    createSession()
      .then((s) => {
        setSessionId(s.session_id)
        setPhase("answering")
      })
      .catch((e: Error) => {
        setErrorMsg(e.message)
        setPhase("error")
      })
  }, [])

  // 用户选择一个答案
  const answer = useCallback(
    async (value: number) => {
      if (!sessionId || phase !== "answering") return

      const question = QUESTIONS[currentIndex]
      const newAnswers = { ...answers, [question.id]: value }
      setAnswers(newAnswers)

      const isLast = currentIndex === QUESTIONS.length - 1

      if (!isLast) {
        setCurrentIndex(currentIndex + 1)
        return
      }

      // 最后一题：提交所有答案，完成测评
      setPhase("submitting")
      try {
        const responses = Object.entries(newAnswers).map(([qid, ans]) => ({
          question_id: qid,
          module: "riasec",
          answer: ans,
        }))
        await submitResponses(sessionId, responses)
        const assessmentResult = await completeSession(sessionId)
        setResult(assessmentResult)
        setPhase("done")
      } catch (e) {
        setErrorMsg((e as Error).message)
        setPhase("error")
      }
    },
    [sessionId, phase, currentIndex, answers]
  )

  return {
    phase,
    currentIndex,
    currentQuestion: QUESTIONS[currentIndex],
    totalQuestions: QUESTIONS.length,
    result,
    errorMsg,
    answer,
  }
}
