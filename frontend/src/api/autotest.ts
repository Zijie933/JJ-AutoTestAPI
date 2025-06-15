import { AnyARecord } from 'dns';
import request, { apiClient } from './index.js';
import type { BackendResponse } from './types.js';

export interface ApiCase {
  id: number;
  name: string;
  description?: string;
  method: 'GET' | 'POST' | 'PUT' | 'DELETE' | 'PATCH' | 'HEAD' | 'OPTIONS'; // Constrain to valid HTTP methods
  url: string;
  headers?: string; // Should be a JSON string
  params?: string;  // Should be a JSON string
  body?: string;    // Should be a JSON string (or other formats like form-data, XML, etc.)
  cookies?: string; // Should be a JSON string
  // Add any other fields that are part of your API case definition
  created_at?: string; // Assuming backend provides these
  updated_at?: string;
}

// Get all API test cases
export const getAllApiCases = (): Promise<ApiCase[]> => {
  return request<ApiCase[]>({ url: '/autotest/list', method: 'GET' });
};

// Create a new API test case
export const createApiCase = (data: Omit<ApiCase, 'id' | 'created_at' | 'updated_at'>): Promise<ApiCase> => {
  return request<ApiCase>({ url: '/autotest/create', method: 'POST', data });
};

// Update an existing API test case
export const updateApiCase = (id: number, data: Partial<Omit<ApiCase, 'id' | 'created_at' | 'updated_at'>>): Promise<ApiCase> => {
  return request<ApiCase>({ url: `/autotest/update`, method: 'PUT', data });
};

// Delete an API test case
export const deleteApiCase = (id: number): Promise<void> => {
  // Assuming the backend returns no content (204) or a simple success message for delete
  // Adjust BackendResponse<void> if it returns something specific
  return request<void>({ url: `/autotest/${id}`, method: 'DELETE' });
};

// Execute an API test case
// The response type 'any' should be replaced with a more specific interface
// representing the structure of the test execution result from your backend.
// Corresponds to the backend's ApiTestCase class
export interface ApiTestCaseData {
  id: number;
  name: string;
  description?: string; // Matches backend, optional
  // project_id is not in backend ApiTestCase model, removing
  url: string;
  method: string; // In backend, will be one of 'GET', 'POST', etc.
  headers?: string; // Backend stores as JSON string
  params?: string;  // Backend stores as JSON string
  body?: string;    // Backend stores as JSON string (or other text like XML)
  cookies?: string; // Backend stores as JSON string
  created_at?: string; // Optional, if backend provides it
  updated_at?: string; // Optional, if backend provides it
  // assert_options, extract_options, priority, tags, status, created_by, updated_by are not directly in ApiTestCase model in backend files shown
  // Keeping them commented out or removed unless confirmed they are part of a flattened structure or extended model
  // priority?: number;
  // tags?: string[];
  // status?: string;
  // created_by?: number;
  // updated_by?: number;
}

// Corresponds to the backend's ApiTestCaseRunResponse class
export interface ApiTestExecutionResult {
  case?: ApiTestCaseData; // Optional, as per backend schema
  running_results: any[]; // List of execution results for each step/assertion
  // Include other fields from the backend response if they are at this level
  // For example, if the backend also returns overall status or duration here:
  // overall_status?: string;
  // total_duration?: number;
}

// Define the AssertCategory enum based on backend schema (common/models/assertModel.py)
export enum AssertCategory {
  STATUS_CODE = "status_code",
  RESPONSE_TIME = "response_time",
  BODY_FIELD = "body_field",
  BODY_TEXT = "body_text",
  HEADER_FIELD = "header_field",
  COOKIES_FIELD = "cookies_field",
  ENV = "env",
}

// Define the AssertOperator enum based on backend schema (common/models/assertModel.py)
export enum AssertOperator {
  EQ = "==",
  NE = "!=",
  GT = ">",
  GE = ">=",
  LT = "<",
  LE = "<=",
  CONTAINS = "contains",
  NOT_CONTAINS = "not_contains",
  REGEX_MATCH = "regex_match",
  EXISTS = "exists",
  NOT_EXISTS = "not_exists",
  STARTS_WITH = "starts_with",
  ENDS_WITH = "ends_with",
}

// Define the Assert interface based on backend schema (common/models/assertModel.py)
export interface Assert {
  category: AssertCategory;
  operator: AssertOperator;
  path?: string | null;
  expected?: any | null;
}

// Define the Example type based on backend schema (common/models/example.py)
export interface Example {
  // Note: In backend, Example is a SQLModel without id, case_id, created_at, updated_at.
  // These fields are typically part of a database table model, not the Pydantic model used for request/response directly within the 'examples' list of ApiTestCaseRunParams.
  // However, if your backend's `examples.py` (which I haven't seen) defines a table model that includes these, then they are fine here.
  // For now, I'll keep them as optional, assuming they might be relevant if an Example can be saved/retrieved independently.
  id?: number;
  name?: string;
  headers?: string | null; // JSON string
  params?: string | null;  // JSON string
  body?: string | null;    // JSON string or other text
  cookies?: string | null; // JSON string
  timeout?: number | null;
  asserts?: Assert[] | null; // Use the more specific Assert type
  // variables?: any[]; // 'variables' is not in the backend Example model (common/models/example.py)
  case_id?: number;
  created_at?: string;
  updated_at?: string;
}

// Define the payload for running a test case, aligning with backend ApiTestCaseRunParams
export interface ApiTestCaseRunPayload {
  id?: number;                 // Existing case ID
  case?: Partial<ApiCase>;    // For running a raw, unsaved case definition
  examples?: Example[];        // List of examples to run with
}

export const runApiTestCase = (payload: ApiTestCaseRunPayload): Promise<ApiTestExecutionResult> => {
  // The endpoint is /autotest/run, and it's a POST request.
  // The payload now directly matches ApiTestCaseRunParams
  return apiClient.post<ApiTestExecutionResult>(`/autotest/run`, payload).then(res => res);
  // Note: The .then(res => res) might be redundant if apiClient.post already returns the desired structure.
  // If apiClient.post returns an AxiosResponse, you might need res.data.
  // Based on previous usage `apiClient.post<...>(...).then(res => res.data.data)` or `then(res => res.data)`
  // Let's assume for now that the direct response `res` is what we need, as per the last successful modification.
  // If it was `res.data` before, it should be `res.data` now.
  // Given the previous successful change was `return apiClient.post<ApiTestExecutionResult>(...).then(res => res);`
  // I will keep it as `res` for consistency, but this is a common point of error if the apiClient wrapper behaves differently.
};