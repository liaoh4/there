interface ButtonProps {
  children: React.ReactNode
  onClick?: () => void
  disabled?: boolean
  variant?: "primary" | "outline"
  className?: string
}

export default function Button({
  children,
  onClick,
  disabled = false,
  variant = "primary",
  className = "",
}: ButtonProps) {
  const base = "px-6 py-3 rounded-xl font-medium transition-all duration-200 cursor-pointer"
  const variants = {
    primary: "bg-indigo-600 text-white hover:bg-indigo-700 disabled:opacity-50",
    outline: "border-2 border-indigo-600 text-indigo-600 hover:bg-indigo-50",
  }

  return (
    <button
      onClick={onClick}
      disabled={disabled}
      className={`${base} ${variants[variant]} ${className}`}
    >
      {children}
    </button>
  )
}
