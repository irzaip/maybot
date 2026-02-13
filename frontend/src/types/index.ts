export enum Persona {
  ASSISTANT = 'ASSISTANT',
  USTAD = 'USTAD',
  HRD = 'HRD',
  CONTENT_MANAGER = 'CONTENT_MANAGER',
  CONTENT_CREATOR = 'CONTENT_CREATOR',
  PSYCHOLOG = 'PSYCHOLOG',
  ROLEPLAY = 'ROLEPLAY',
  VOLD = 'VOLD',
  INDOSOAI = 'INDOSOAI',
  KOBOLD = 'KOBOLD',
  SALES_CS = 'SALES_CS',
  KOS_CS = 'KOS_CS',
  FIT_TRAINER = 'FIT_TRAINER'
}

export enum ConvType {
  DEMO = 'DEMO',
  FRIEND = 'FRIEND',
  GOLD = 'GOLD',
  PLATINUM = 'PLATINUM',
  ADMIN = 'ADMIN'
}

export enum ConvMode {
  CHITCHAT = 'CHITCHAT',
  ASK = 'ASK',
  THINK = 'THINK',
  QUIZ = 'QUIZ',
  TIMED = 'TIMED',
  INTERVIEW = 'INTERVIEW',
  YESNO = 'YESNO',
  CHAIN = 'CHAIN'
}

export enum Role {
  SYSTEM = 'SYSTEM',
  USER = 'USER',
  ASSISTANT = 'ASSISTANT'
}

export enum Script {
  BRAIN = 'BRAIN',
  DEPARSE = 'DEPARSE',
  JS_OBJECTS = 'JS_OBJECTS',
  JSON_SERVER = 'JSON_SERVER',
  PARSER = 'PARSER',
  SESSIONS = 'SESSIONS',
  NEWCOMER = 'NEWCOMER',
  INTERVIEW = 'INTERVIEW'
}

export interface Message {
  text: string
  user_number: string
  bot_number: string
  timestamp: number
  notifyName?: string
  type: string
  client?: string
  author?: string
  hasMedia?: boolean
  message?: any
}

export interface BotQuestion {
  id: number
  question: string
  answer: string
  metadata?: any
  koherensi?: number
  multiplier?: number
  score?: number
  comment?: string
}

export interface MessageContent {
  user_number: string
  bot_number: string
  message: string
  role: Role
}

export interface Conversation {
  user_number: string
  bot_number: string
  bot_name?: string
  user_name?: string
  persona: Persona
  convtype: ConvType
  convmode: ConvMode
  script?: Script
  temperature: number
  interval: number
  wait_time?: number
  messages: Array<{ role: Role; content: string }>
  botquestions: BotQuestion[]
  intro_msg?: string
  outro_msg?: string
  WORD_LIMIT: number
  free_tries: number
  demo_user: boolean
  need_group_prefix: boolean
  group_title?: string
  gpt_accessed: number
  gpt_token_used: number
  daily_free_gpt: number
  intro_maxs_free_gpt: number
  paid_messages: number
  free_gpt: boolean
  profanity_counter: number
  funny_counter: number
  promo_counter: number
  max_promo: number
  max_funny: number
  profanity: boolean
  anti_flood: any[]
  last_question?: string
  question_asked?: string
  user_fullinfo?: any
}

export interface DashboardStats {
  active_conversations: number
  maintenance_mode: boolean
  server_status: string
  total_messages: number
  token_usage: number
  error_count?: number
  uptime?: number
}

export interface ConversationListItem {
  user_number: string
  user_name: string
  bot_name?: string
  persona: Persona
  convmode: ConvMode
  convtype: ConvType
  free_tries: number
  paid_messages: number
  last_active?: string
  message_count: number
}

export interface BulkOperationRequest {
  user_numbers: string[]
  persona?: Persona
  convmode?: ConvMode
  convtype?: ConvType
  action: string
}

export interface WebSocketMessage {
  type: string
  data: any
  timestamp?: string
}