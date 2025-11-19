/**
 * API Client for Website Migration Platform
 *
 * Provides typed methods for interacting with the backend API
 */

import axios, { AxiosInstance } from 'axios';
import {
  Migration,
  MigrationCreateRequest,
  MigrationResponse,
  SimilarityReport,
  IDF,
  DeploymentRequest,
} from '@/types';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

class MigrationAPI {
  private client: AxiosInstance;

  constructor(baseURL: string = API_BASE_URL) {
    this.client = axios.create({
      baseURL,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Request interceptor for auth
    this.client.interceptors.request.use((config) => {
      const token = localStorage.getItem('auth_token');
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
      return config;
    });

    // Response interceptor for error handling
    this.client.interceptors.response.use(
      (response) => response,
      (error) => {
        console.error('API Error:', error.response?.data || error.message);
        throw error;
      }
    );
  }

  // ============================================================================
  // Migration Endpoints
  // ============================================================================

  /**
   * Create a new migration
   */
  async createMigration(data: MigrationCreateRequest): Promise<MigrationResponse> {
    const response = await this.client.post<MigrationResponse>('/api/v1/migrations', data);
    return response.data;
  }

  /**
   * List all migrations
   */
  async listMigrations(params?: {
    skip?: number;
    limit?: number;
    status?: string;
  }): Promise<MigrationResponse[]> {
    const response = await this.client.get<MigrationResponse[]>('/api/v1/migrations', {
      params,
    });
    return response.data;
  }

  /**
   * Get a specific migration by ID
   */
  async getMigration(migrationId: string): Promise<MigrationResponse> {
    const response = await this.client.get<MigrationResponse>(
      `/api/v1/migrations/${migrationId}`
    );
    return response.data;
  }

  /**
   * Delete a migration
   */
  async deleteMigration(migrationId: string): Promise<{ message: string; id: string }> {
    const response = await this.client.delete(`/api/v1/migrations/${migrationId}`);
    return response.data;
  }

  /**
   * Get IDF (Intermediate Data Format) for a migration
   */
  async getMigrationIDF(migrationId: string): Promise<IDF> {
    const response = await this.client.get<IDF>(`/api/v1/migrations/${migrationId}/idf`);
    return response.data;
  }

  /**
   * Get converted data (WordPress/Elementor format)
   */
  async getConvertedData(migrationId: string): Promise<any> {
    const response = await this.client.get(`/api/v1/migrations/${migrationId}/converted`);
    return response.data;
  }

  /**
   * Get similarity report for a migration
   */
  async getSimilarityReport(migrationId: string): Promise<SimilarityReport> {
    const response = await this.client.get<SimilarityReport>(
      `/api/v1/migrations/${migrationId}/similarity`
    );
    return response.data;
  }

  /**
   * Run validation and similarity check
   */
  async validateMigration(migrationId: string): Promise<{ message: string; migration_id: string }> {
    const response = await this.client.post(`/api/v1/migrations/${migrationId}/validate`);
    return response.data;
  }

  /**
   * AI-powered editing with natural language
   */
  async aiEdit(
    migrationId: string,
    prompt: string,
    pageId?: string
  ): Promise<{ message: string; migration_id: string; prompt: string }> {
    const response = await this.client.post(`/api/v1/migrations/${migrationId}/ai-edit`, {
      prompt,
      page_id: pageId,
    });
    return response.data;
  }

  /**
   * Deploy migration to hosting
   */
  async deployMigration(
    migrationId: string,
    data: DeploymentRequest
  ): Promise<{ message: string; migration_id: string; hosting_provider: string }> {
    const response = await this.client.post(`/api/v1/migrations/${migrationId}/deploy`, data);
    return response.data;
  }

  /**
   * Get preview URL for migrated site
   */
  async getPreviewUrl(
    migrationId: string
  ): Promise<{ migration_id: string; preview_url: string; expires_at: string }> {
    const response = await this.client.get(`/api/v1/migrations/${migrationId}/preview`);
    return response.data;
  }

  // ============================================================================
  // Utility Endpoints
  // ============================================================================

  /**
   * Get supported platforms
   */
  async getSupportedPlatforms(): Promise<{
    source_platforms: Array<{ value: string; name: string }>;
    target_platforms: Array<{ value: string; name: string }>;
  }> {
    const response = await this.client.get('/api/v1/platforms');
    return response.data;
  }

  /**
   * Health check
   */
  async healthCheck(): Promise<{
    status: string;
    database: string;
    ai_services: string;
    timestamp: string;
  }> {
    const response = await this.client.get('/health');
    return response.data;
  }

  // ============================================================================
  // WebSocket for Real-time Updates (Future)
  // ============================================================================

  /**
   * Subscribe to migration updates via WebSocket
   * TODO: Implement WebSocket connection for real-time progress updates
   */
  subscribeMigrationUpdates(migrationId: string, callback: (data: any) => void): () => void {
    // Placeholder for WebSocket implementation
    console.log('WebSocket subscription not yet implemented');

    // Return unsubscribe function
    return () => {
      console.log('Unsubscribed from migration updates');
    };
  }
}

// Export singleton instance
export const migrationApi = new MigrationAPI();

// Export class for custom instances
export { MigrationAPI };
