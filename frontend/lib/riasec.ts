import type { RiasecDimension } from "./types"

export interface DimensionInfo {
  key: RiasecDimension
  name: string        // 中文名
  description: string // 简短描述，显示在结果页
  color: string       // Tailwind 颜色类，用于雷达图和标签
}

export const DIMENSIONS: DimensionInfo[] = [
  {
    key: "R",
    name: "实践型",
    description: "喜欢动手操作、机械工具和户外活动",
    color: "#f97316",  // orange
  },
  {
    key: "I",
    name: "研究型",
    description: "喜欢分析思考、解决抽象问题和科学探究",
    color: "#3b82f6",  // blue
  },
  {
    key: "A",
    name: "艺术型",
    description: "喜欢创意表达、审美设计和自由发挥",
    color: "#a855f7",  // purple
  },
  {
    key: "S",
    name: "社会型",
    description: "喜欢帮助他人、教学沟通和团队合作",
    color: "#22c55e",  // green
  },
  {
    key: "E",
    name: "企业型",
    description: "喜欢领导管理、说服他人和追求目标",
    color: "#ef4444",  // red
  },
  {
    key: "C",
    name: "传统型",
    description: "喜欢有序规则、数据处理和细致执行",
    color: "#eab308",  // yellow
  },
]

export const DIMENSION_MAP = Object.fromEntries(
  DIMENSIONS.map((d) => [d.key, d])
) as Record<RiasecDimension, DimensionInfo>
