/**
 * TypeScript Types for Website Migration Platform
 */

// ============================================================================
// Migration Types
// ============================================================================

export type MigrationStatus =
  | 'pending'
  | 'extracting'
  | 'analyzing'
  | 'converting'
  | 'validating'
  | 'completed'
  | 'failed';

export type SourcePlatform = 'wix' | 'squarespace' | 'webflow' | 'wordpress' | 'custom_html';

export type TargetPlatform = 'wordpress_elementor' | 'wordpress' | 'squarespace' | 'duda';

export interface Migration {
  id: string;
  project_name: string;
  source_url: string;
  source_platform: SourcePlatform;
  target_platform: TargetPlatform;
  status: MigrationStatus;
  progress: number;
  current_step?: string;
  similarity_score?: number;
  created_at: string;
  updated_at: string;
  completed_at?: string;
  deployment_url?: string;
  error_message?: string;
}

export interface MigrationCreateRequest {
  project_name: string;
  source_url: string;
  source_platform: SourcePlatform;
  target_platform: TargetPlatform;
  client_email?: string;
}

export interface MigrationResponse extends Migration {}

// ============================================================================
// IDF (Intermediate Data Format) Types
// ============================================================================

export type ElementType =
  | 'container'
  | 'section'
  | 'row'
  | 'column'
  | 'header'
  | 'footer'
  | 'navigation'
  | 'menu'
  | 'menu_item'
  | 'text'
  | 'heading'
  | 'paragraph'
  | 'list'
  | 'list_item'
  | 'image'
  | 'video'
  | 'audio'
  | 'gallery'
  | 'slider'
  | 'button'
  | 'link'
  | 'form'
  | 'input'
  | 'textarea'
  | 'select'
  | 'checkbox'
  | 'radio'
  | 'hero'
  | 'card'
  | 'accordion'
  | 'tab'
  | 'modal'
  | 'icon'
  | 'spacer'
  | 'divider'
  | 'iframe'
  | 'embed'
  | 'html'
  | 'script';

export interface Element {
  id: string;
  type: ElementType;
  tag?: string;
  content?: string;
  html?: string;
  classes: string[];
  styles: Record<string, any>;
  responsive_styles?: ResponsiveStyles;
  children: Element[];
  parent_id?: string;
  order: number;
  attributes: Record<string, any>;
  assets: Asset[];
  animations: Animation[];
  interactions: Interaction[];
  metadata: Record<string, any>;
  platform_data: Record<string, any>;
}

export interface ResponsiveStyles {
  desktop: Record<string, any>;
  tablet: Record<string, any>;
  mobile: Record<string, any>;
}

export interface Animation {
  name: string;
  duration: number;
  delay: number;
  timing_function: string;
  iteration_count: number | string;
  direction: string;
  fill_mode: string;
}

export interface Interaction {
  event: string;
  action: string;
  target?: string;
  parameters: Record<string, any>;
}

export interface Asset {
  id: string;
  type: string;
  original_url: string;
  local_path?: string;
  s3_url?: string;
  width?: number;
  height?: number;
  size?: number;
  mime_type?: string;
  alt_text?: string;
  metadata: Record<string, any>;
}

export interface SEOData {
  title?: string;
  description?: string;
  keywords: string[];
  canonical_url?: string;
  og_title?: string;
  og_description?: string;
  og_image?: string;
  og_type?: string;
  twitter_card?: string;
  twitter_title?: string;
  twitter_description?: string;
  twitter_image?: string;
  structured_data: any[];
  robots?: string;
}

export interface Page {
  id: string;
  title: string;
  slug: string;
  path: string;
  elements: Element[];
  seo: SEOData;
  is_homepage: boolean;
  template?: string;
  parent_page_id?: string;
  order: number;
  published: boolean;
  created_at?: string;
  updated_at?: string;
  platform_data: Record<string, any>;
}

export interface ColorPalette {
  primary: string;
  secondary?: string;
  accent?: string;
  background: string;
  text: string;
  custom_colors: Record<string, string>;
}

export interface Font {
  id: string;
  family: string;
  variants: string[];
  source: string;
  url?: string;
  local_path?: string;
}

export interface Theme {
  name: string;
  colors: ColorPalette;
  fonts: Font[];
  spacing: Record<string, number>;
  breakpoints: Record<string, number>;
  custom_css?: string;
}

export interface GlobalSettings {
  site_name: string;
  site_url: string;
  language: string;
  favicon?: Asset;
  logo?: Asset;
  google_analytics_id?: string;
  google_tag_manager_id?: string;
  facebook_pixel_id?: string;
  social_links: Record<string, string>;
  contact_email?: string;
  contact_phone?: string;
  custom_head_code?: string;
  custom_footer_code?: string;
}

export interface IDF {
  id: string;
  version: string;
  created_at: string;
  updated_at: string;
  source_platform: string;
  source_url: string;
  pages: Page[];
  theme: Theme;
  settings: GlobalSettings;
  assets: Asset[];
  navigation: Record<string, any>;
  extraction_metadata: Record<string, any>;
  similarity_scores: Record<string, number>;
  platform_data: Record<string, any>;
}

// ============================================================================
// Similarity & Quality Check Types
// ============================================================================

export interface SimilarityScores {
  visual: { score: number; details?: any };
  structural: { score: number; details?: any };
  content: { score: number; details?: any };
  asset: { score: number; details?: any };
  semantic: { score: number; details?: any };
}

export interface SimilarityReport {
  migration_id: string;
  similarity_score: number;
  report: {
    overall_score: number;
    meets_target: boolean;
    target_score: number;
    scores: SimilarityScores;
    details: Record<string, any>;
    recommendations: string[];
  };
}

// ============================================================================
// Deployment Types
// ============================================================================

export interface DeploymentRequest {
  hosting_provider: string;
  domain?: string;
  credentials?: Record<string, any>;
}

// ============================================================================
// User & Authentication Types
// ============================================================================

export interface User {
  id: string;
  email: string;
  name: string;
  plan: 'free' | 'pro' | 'enterprise';
  migrations_limit: number;
  migrations_used: number;
  created_at: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: User;
}

// ============================================================================
// Platform Configuration
// ============================================================================

export interface PlatformOption {
  value: string;
  name: string;
  description?: string;
  icon?: string;
}

export interface PlatformsResponse {
  source_platforms: PlatformOption[];
  target_platforms: PlatformOption[];
}
