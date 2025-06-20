export interface SegmentationResult {
  original_image: string;
  segmented_image: string;
  filename?: string;
  source_url?: string;
}

export interface ApiError {
  detail: string;
}

export interface AxiosErrorResponse {
  response?: {
    data?: {
      detail?: string;
    };
  };
}