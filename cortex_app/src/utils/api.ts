import config from "../config";

// Tipos para el nuevo sistema
export interface QueryLogSummary {
  id: number;
  title: string | null;
  question: string;
  is_executable: boolean;
  attempts_count: number;
  timestamp: string;
}

export interface QueryLogDetail {
  id: number;
  title: string | null;
  question: string;
  medical_terms: string[] | null;
  generated_sql: string | null;
  is_executable: boolean;
  attempts_count: number;
  error_message: string | null;
  processing_time: number | null;
  results_count: number | null;
  timestamp: string;
}

class ApiService {
  private getAuthHeaders(token?: string | null): Record<string, string> {
    const headers: Record<string, string> = {
      "Content-Type": "application/json",
    };
    
    if (token) {
      headers["Authorization"] = `Bearer ${token}`;
    }
    
    return headers;
  }

  // Métodos existentes (mantener compatibilidad)
  async get(endpoint: string, token?: string | null) {
    const response = await fetch(`${config.API_BASE_URL}${endpoint}`, {
      method: "GET",
      headers: this.getAuthHeaders(token),
    });

    if (!response.ok) {
      throw new Error(`API Error: ${response.status}`);
    }

    return response.json();
  }

  async post(endpoint: string, data: any, token?: string | null) {
    const response = await fetch(`${config.API_BASE_URL}${endpoint}`, {
      method: "POST",
      headers: this.getAuthHeaders(token),
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      throw new Error(`API Error: ${response.status}`);
    }

    return response.json();
  }

  // Nuevos métodos específicos para el historial mejorado
  async getQueryHistory(token: string, limit: number = 50, offset: number = 0): Promise<QueryLogSummary[]> {
    const response = await fetch(`${config.API_BASE_URL}/queries/history?limit=${limit}&offset=${offset}`, {
      method: "GET",
      headers: this.getAuthHeaders(token),
    });

    if (!response.ok) {
      throw new Error(`Error obteniendo historial: ${response.status}`);
    }

    return response.json();
  }

  async getQueryDetails(queryId: number, token: string): Promise<QueryLogDetail> {
    const response = await fetch(`${config.API_BASE_URL}/queries/${queryId}`, {
      method: "GET",
      headers: this.getAuthHeaders(token),
    });

    if (!response.ok) {
      throw new Error(`Error obteniendo detalles: ${response.status}`);
    }

    return response.json();
  }

  async deleteQuery(queryId: number, token: string): Promise<void> {
    const response = await fetch(`${config.API_BASE_URL}/queries/${queryId}`, {
      method: "DELETE",
      headers: this.getAuthHeaders(token),
    });

    if (!response.ok) {
      throw new Error(`Error eliminando consulta: ${response.status}`);
    }
  }

  // Método para generar SQL (ya no necesita guardar manualmente, se hace automáticamente)
  async generateSQL(question: string, medicalTerms: any[], token: string) {
    const response = await fetch(`${config.API_BASE_URL}/sql-generation/`, {
      method: "POST",
      headers: this.getAuthHeaders(token),
      body: JSON.stringify({
        question,
        medical_terms: medicalTerms
      }),
    });

    if (!response.ok) {
      throw new Error(`Error generando SQL: ${response.status}`);
    }

    return response.json();
  }

  // Métodos médicos existentes
  async extractEntities(text: string, language: 'es' | 'en' = 'es', token?: string | null) {
    const endpoint = language === 'es' ? '/extractEs' : '/extract';
    const response = await fetch(`${config.API_BASE_URL}${endpoint}`, {
      method: "POST",
      headers: this.getAuthHeaders(token),
      body: JSON.stringify({ text }),
    });

    if (!response.ok) {
      throw new Error("Error al extraer términos");
    }

    const data = await response.json();
    return data.entities;
  }

  async getSimilarTerms(term: string, token?: string | null) {
    const response = await fetch(`${config.API_BASE_URL}/similar_db`, {
      method: "POST",
      headers: this.getAuthHeaders(token),
      body: JSON.stringify({ term }),
    });

    if (!response.ok) {
      throw new Error("Error obteniendo términos similares");
    }

    const data = await response.json();
    return data.results;
  }
}

export const api = new ApiService();