import type { RiasecDimension } from "./types"

export interface Question {
  id: string
  dimension: RiasecDimension
  text: string
}

export const QUESTIONS: Question[] = [
  // R — 实践型：喜欢动手操作、机械、户外活动
  { id: "r1", dimension: "R", text: "我喜欢动手操作机械、工具或电子设备" },
  { id: "r2", dimension: "R", text: "我更喜欢在户外或实验室工作，而不是坐在办公室" },

  // I — 研究型：喜欢分析、研究、解决抽象问题
  { id: "i1", dimension: "I", text: "我喜欢研究和分析复杂的问题，哪怕需要很长时间" },
  { id: "i2", dimension: "I", text: "我对科学原理和数学逻辑感到着迷" },

  // A — 艺术型：喜欢创作、表达、不喜欢规则约束
  { id: "a1", dimension: "A", text: "我喜欢通过绘画、写作、音乐或设计来表达自己" },
  { id: "a2", dimension: "A", text: "我更愿意用创意解决问题，而不是按固定步骤操作" },

  // S — 社会型：喜欢帮助他人、教学、团队合作
  { id: "s1", dimension: "S", text: "我享受帮助他人解决问题，或者教别人学习新技能" },
  { id: "s2", dimension: "S", text: "与人沟通和建立关系是我擅长并享受的事" },

  // E — 企业型：喜欢领导、说服、管理
  { id: "e1", dimension: "E", text: "我喜欢组织活动、带领团队，并说服他人接受我的想法" },
  { id: "e2", dimension: "E", text: "我对商业机会很敏感，愿意为了目标承担风险" },

  // C — 传统型：喜欢有序、规则、数据处理
  { id: "c1", dimension: "C", text: "我喜欢按照明确的规则和流程完成任务" },
  { id: "c2", dimension: "C", text: "处理数据、文件或财务记录让我感到踏实有条理" },
]

export const TOTAL_QUESTIONS = QUESTIONS.length  // 12
