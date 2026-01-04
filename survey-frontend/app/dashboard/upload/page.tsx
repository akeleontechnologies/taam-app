'use client';

import { useState } from 'react';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { UploadCloud, FileText, CheckCircle2, XCircle, Trash2 } from 'lucide-react';
import axios from 'axios';
import { API_ENDPOINTS, getAuthHeaders } from '@/lib/api';
import toast from 'react-hot-toast';

interface FileWithStatus {
  id: string;
  file: File;
  status: 'pending' | 'uploading' | 'success' | 'error';
  message?: string;
}

export default function UploadPage() {
  const [selectedFiles, setSelectedFiles] = useState<FileWithStatus[]>([]);
  const [isDragging, setIsDragging] = useState(false);
  const [uploading, setUploading] = useState(false);

  const handleFileSelect = (files: FileList | null) => {
    if (!files) return;

    const newFiles: FileWithStatus[] = Array.from(files).map((file) => ({
      id: `${file.name}-${Date.now()}-${Math.random()}`,
      file,
      status: 'pending' as const,
    }));

    setSelectedFiles((prev) => [...prev, ...newFiles]);
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    handleFileSelect(e.target.files);
    // Reset input so same file can be selected again
    e.target.value = '';
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    handleFileSelect(e.dataTransfer.files);
  };

  const removeFile = (id: string) => {
    setSelectedFiles((prev) => prev.filter((f) => f.id !== id));
  };

  const uploadSingleFile = async (fileWithStatus: FileWithStatus) => {
    const formData = new FormData();
    formData.append('file', fileWithStatus.file);

    try {
      const authHeaders = getAuthHeaders();
      const response = await axios.post(API_ENDPOINTS.datasets.upload, formData, {
        headers: authHeaders,
      });

      return {
        success: true,
        message: `Uploaded successfully! Dataset: ${response.data.dataset?.filename || 'Unknown'}`,
      };
    } catch (error: unknown) {
      const err = error as {response?: {data?: {error?: string; file?: string[]; detail?: string}}};
      console.error('Upload error:', err.response?.data);
      const errorMsg =
        err.response?.data?.error ||
        err.response?.data?.file?.[0] ||
        err.response?.data?.detail ||
        'Failed to upload file';
      return {
        success: false,
        message: errorMsg,
      };
    }
  };

  const handleUploadAll = async () => {
    if (selectedFiles.length === 0) {
      toast.error('Please select at least one file');
      return;
    }

    setUploading(true);

    // Update all to uploading status
    setSelectedFiles((prev) =>
      prev.map((f) => ({ ...f, status: 'uploading' as const }))
    );

    let successCount = 0;
    let errorCount = 0;

    // Upload files sequentially to avoid overwhelming the server
    for (const fileWithStatus of selectedFiles) {
      const result = await uploadSingleFile(fileWithStatus);

      setSelectedFiles((prev) =>
        prev.map((f) =>
          f.id === fileWithStatus.id
            ? {
                ...f,
                status: result.success ? 'success' : 'error',
                message: result.message,
              }
            : f
        )
      );

      if (result.success) {
        successCount++;
      } else {
        errorCount++;
      }
    }

    setUploading(false);

    // Show summary toast
    if (successCount > 0 && errorCount === 0) {
      toast.success(`All ${successCount} file(s) uploaded successfully!`);
    } else if (successCount > 0 && errorCount > 0) {
      toast.success(`${successCount} file(s) uploaded, ${errorCount} failed`);
    } else {
      toast.error('All uploads failed');
    }
  };

  const clearCompleted = () => {
    setSelectedFiles((prev) => prev.filter((f) => f.status !== 'success'));
  };

  const clearAll = () => {
    setSelectedFiles([]);
  };

  const pendingFiles = selectedFiles.filter((f) => f.status === 'pending');
  const completedFiles = selectedFiles.filter((f) => f.status === 'success');
  const failedFiles = selectedFiles.filter((f) => f.status === 'error');

  return (
    <div className="max-w-4xl mx-auto">
      <h1 className="text-3xl font-bold text-gray-900 mb-2">Upload Data</h1>
      <p className="text-gray-600 mb-8">
        Upload your CSV or XLSX survey data files for analysis (multiple files supported)
      </p>

      <Card className="p-8">
        <div className="space-y-6">
          {/* File Upload Area with Drag & Drop */}
          <div
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
            className={`border-2 border-dashed rounded-lg p-12 text-center transition-all ${
              isDragging
                ? 'border-blue-500 bg-blue-50'
                : 'border-gray-300 hover:border-blue-400'
            }`}
          >
            <UploadCloud
              className={`h-12 w-12 mx-auto mb-4 ${
                isDragging ? 'text-blue-500' : 'text-gray-400'
              }`}
            />
            <div className="space-y-2">
              <label
                htmlFor="file-upload"
                className="cursor-pointer text-blue-600 hover:text-blue-700 font-medium"
              >
                Click to upload
              </label>
              <Input
                id="file-upload"
                type="file"
                accept=".csv,.xlsx,.xls"
                onChange={handleFileChange}
                className="hidden"
                multiple
              />
              <p className="text-sm text-gray-500">
                or drag and drop <span className="font-medium">multiple files</span>
              </p>
              <p className="text-xs text-gray-400">CSV or XLSX files (max 20MB each)</p>
            </div>
          </div>

          {/* Selected Files List */}
          {selectedFiles.length > 0 && (
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <h3 className="font-semibold text-gray-900">
                  Selected Files ({selectedFiles.length})
                </h3>
                <div className="flex gap-2">
                  {completedFiles.length > 0 && (
                    <Button onClick={clearCompleted} variant="outline" size="sm">
                      Clear Completed
                    </Button>
                  )}
                  <Button onClick={clearAll} variant="outline" size="sm">
                    Clear All
                  </Button>
                </div>
              </div>

              <div className="space-y-2 max-h-96 overflow-y-auto">
                {selectedFiles.map((fileWithStatus) => (
                  <div
                    key={fileWithStatus.id}
                    className={`flex items-center gap-3 p-4 rounded-lg border ${
                      fileWithStatus.status === 'success'
                        ? 'bg-green-50 border-green-200'
                        : fileWithStatus.status === 'error'
                        ? 'bg-red-50 border-red-200'
                        : fileWithStatus.status === 'uploading'
                        ? 'bg-blue-50 border-blue-200'
                        : 'bg-gray-50 border-gray-200'
                    }`}
                  >
                    {fileWithStatus.status === 'success' ? (
                      <CheckCircle2 className="h-5 w-5 text-green-600 flex-shrink-0" />
                    ) : fileWithStatus.status === 'error' ? (
                      <XCircle className="h-5 w-5 text-red-600 flex-shrink-0" />
                    ) : fileWithStatus.status === 'uploading' ? (
                      <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-blue-600 flex-shrink-0" />
                    ) : (
                      <FileText className="h-5 w-5 text-blue-600 flex-shrink-0" />
                    )}

                    <div className="flex-1 min-w-0">
                      <p className="font-medium text-gray-900 truncate">
                        {fileWithStatus.file.name}
                      </p>
                      <div className="flex items-center gap-3 text-sm">
                        <span className="text-gray-500">
                          {(fileWithStatus.file.size / 1024 / 1024).toFixed(2)} MB
                        </span>
                        {fileWithStatus.message && (
                          <>
                            <span className="text-gray-400">•</span>
                            <span
                              className={
                                fileWithStatus.status === 'success'
                                  ? 'text-green-700'
                                  : fileWithStatus.status === 'error'
                                  ? 'text-red-700'
                                  : 'text-gray-600'
                              }
                            >
                              {fileWithStatus.message}
                            </span>
                          </>
                        )}
                      </div>
                    </div>

                    {fileWithStatus.status === 'pending' && (
                      <Button
                        onClick={() => removeFile(fileWithStatus.id)}
                        variant="outline"
                        size="sm"
                      >
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Summary Stats */}
          {selectedFiles.length > 0 && (
            <div className="flex gap-4 text-sm">
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 rounded-full bg-gray-300" />
                <span className="text-gray-600">Pending: {pendingFiles.length}</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 rounded-full bg-green-500" />
                <span className="text-gray-600">Completed: {completedFiles.length}</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 rounded-full bg-red-500" />
                <span className="text-gray-600">Failed: {failedFiles.length}</span>
              </div>
            </div>
          )}

          {/* Upload Button */}
          <Button
            onClick={handleUploadAll}
            disabled={selectedFiles.length === 0 || uploading}
            className="w-full"
            size="lg"
          >
            {uploading ? (
              <>
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2" />
                Uploading {selectedFiles.length} file(s)...
              </>
            ) : (
              <>
                <UploadCloud className="h-4 w-4 mr-2" />
                Upload {selectedFiles.length > 0 ? `${selectedFiles.length} ` : ''}File
                {selectedFiles.length !== 1 ? 's' : ''}
              </>
            )}
          </Button>
        </div>
      </Card>

      {/* Instructions */}
      <div className="mt-8 space-y-4">
        <h2 className="text-lg font-semibold text-gray-900">File Requirements</h2>
        <ul className="space-y-2 text-sm text-gray-600">
          <li className="flex items-start gap-2">
            <span className="text-blue-600 mt-0.5">•</span>
            <span>Supported formats: CSV (.csv) and Excel (.xlsx, .xls)</span>
          </li>
          <li className="flex items-start gap-2">
            <span className="text-blue-600 mt-0.5">•</span>
            <span>Maximum file size: 20MB per file</span>
          </li>
          <li className="flex items-start gap-2">
            <span className="text-blue-600 mt-0.5">•</span>
            <span>You can upload multiple files at once by selecting them or dragging and dropping</span>
          </li>
          <li className="flex items-start gap-2">
            <span className="text-blue-600 mt-0.5">•</span>
            <span>
              For TAAM analysis, ensure your file contains the required question columns
              (Q8-Q23)
            </span>
          </li>
          <li className="flex items-start gap-2">
            <span className="text-blue-600 mt-0.5">•</span>
            <span>First row should contain column headers</span>
          </li>
        </ul>
      </div>
    </div>
  );
}
