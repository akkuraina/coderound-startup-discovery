// Types for the application
export interface User {
  id: number;
  email: string;
  name: string;
  is_active: boolean;
  created_at: string;
  last_login?: string;
}

export interface Company {
  id: number;
  name: string;
  website?: string;
  linkedin_url?: string;
  funding_amount?: number;
  funding_date?: string;
  funding_round?: string;
  sector?: string; // e.g., "AI/ML", "Fintech", "Climate Tech"
  is_tech: boolean; // Indicates if company is tech-focused
  investors?: string;
  country?: string;
  description?: string;
  hiring_status: number; // 0=not_hiring, 1=potentially, 2=actively
  hiring_positions?: string;
  enriched_data?: Record<string, any>;
  decision_makers?: {
    decision_makers?: Array<{
      name: string;
      title: string;
      linkedin_url?: string;
    }>;
    confidence?: number;
    enriched_at?: string;
  };
  created_at: string;
  updated_at: string;
  last_enriched?: string;
}

export interface Outreach {
  id: number;
  user_id: number;
  company_id: number;
  email_sent_to: string;
  email_subject: string;
  email_content: string;
  response_status: number; // 0=pending, 1=positive, 2=negative, 3=no_response
  response_received_at?: string;
  response_notes?: string;
  sent_at: string;
  created_at: string;
}

export interface AuthToken {
  access_token: string;
  token_type: string;
  user: User;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface SignupRequest {
  email: string;
  password: string;
  name: string;
}

export interface OutreachRequest {
  company_id: number;
  email_sent_to: string;
  email_subject: string;
  email_content: string;
}

export interface DiscoveryResult {
  companies: Company[];
  total_found: number;
  processed_at: string;
  message: string;
}

export interface EmailTemplate {
  subject: string;
  body: string;
  company_id: number;
  company_name: string;
}
