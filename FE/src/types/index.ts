export type UserRole = 'admin' | 'technician'

export type CaseStatus = 'open' | 'in_progress' | 'awaiting_payment' | 'closed'

export type CasePriority = 'low' | 'normal' | 'urgent'

export interface User {
  id: number
  username: string
  role: UserRole
  must_change_password: boolean
}

export interface LoginResponse {
  user: User
  notifications: string[]
}

export interface CaseListItem {
  id: number
  ticket_number: string
  customer_name: string
  customer_phone: string
  device_type: string
  device_brand: string
  device_model: string
  status: CaseStatus
  priority: CasePriority
  assigned_to_username: string | null
  created_at: string
}

export interface CaseListResponse {
  items: CaseListItem[]
  total: number
}
