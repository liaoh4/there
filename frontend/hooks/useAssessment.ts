"use client"

import { useCallback, useEffect, useRef, useState } from "react"

import {
  completeSession,
  createSession,
  getNextInterestRound,
  submitInterestRound,
  submitResponses,
} from "@/lib/api"
import { drawQuestions, type Question } from "@/lib/questions"
import type { AssessmentResult, InterestRoundResponse } from "@/lib/types"

type Phase = "loading" | "interest" | "riasec" | "submitting" | "done" | "error"

export function useAssessment() {
  const [sessionId, setSessionId] = useState<string | null>(null)
  const [phase, setPhase] = useState<Phase>("loading")
  const [isProcessing, setIsProcessing] = useState(false)

  // Interest phase
  const [currentRound, setCurrentRound] = useState<InterestRoundResponse | null>(null)

  // RIASEC phase
  const [questions, setQuestions] = useState<Question[]>([])
  const [questionIndex, setQuestionIndex] = useState(0)
  const [answers, setAnswers] = useState<Record<string, number>>({})

  const [result, setResult] = useState<AssessmentResult | null>(null)
  const [errorMsg, setErrorMsg] = useState<string | null>(null)

  const creatingRef = useRef(false)

  useEffect(() => {
    if (creatingRef.current) return
    creatingRef.current = true

    async function init() {
      try {
        const session = await createSession()
        const firstRound = await getNextInterestRound(session.session_id)
        setSessionId(session.session_id)
        setCurrentRound(firstRound)
        setPhase("interest")
      } catch (e) {
        setErrorMsg((e as Error).message)
        setPhase("error")
      }
    }

    init()
  }, [])

  const selectCategory = useCallback(
    async (categoryCode: string) => {
      if (!sessionId || !currentRound || isProcessing) return
      setIsProcessing(true)
      try {
        const res = await submitInterestRound(sessionId, {
          round_number: currentRound.round_number,
          selected_category_code: categoryCode,
          presented_category_codes: currentRound.options.map((o) => o.category_code),
          presented_sample_codes: currentRound.options.map((o) => o.sample.code),
        })
        if (res.should_stop) {
          setQuestions(drawQuestions())
          setQuestionIndex(0)
          setAnswers({})
          setPhase("riasec")
        } else if (res.next_round) {
          setCurrentRound(res.next_round)
        }
      } catch (e) {
        setErrorMsg((e as Error).message)
        setPhase("error")
      } finally {
        setIsProcessing(false)
      }
    },
    [sessionId, currentRound, isProcessing]
  )

  const answer = useCallback(
    async (value: number) => {
      if (!sessionId || phase !== "riasec") return

      const question = questions[questionIndex]
      const newAnswers = { ...answers, [question.id]: value }
      setAnswers(newAnswers)

      const isLast = questionIndex === questions.length - 1

      if (!isLast) {
        setQuestionIndex(questionIndex + 1)
        return
      }

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
    [sessionId, phase, questions, questionIndex, answers]
  )

  return {
    phase,
    isProcessing,
    currentRound,
    currentQuestion: questions[questionIndex] ?? null,
    questionIndex,
    totalQuestions: questions.length,
    result,
    errorMsg,
    selectCategory,
    answer,
  }
}
