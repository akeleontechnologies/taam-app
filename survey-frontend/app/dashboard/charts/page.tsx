'use client';

import { useState, useEffect } from 'react';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { DeleteConfirmationDialog } from '@/components/ui/delete-confirmation-dialog';
import { DeleteAllConfirmationDialog } from '@/components/ui/delete-all-confirmation-dialog';
import { BarChart3, Loader2, Eye, Trash2 } from 'lucide-react';
import axios from 'axios';
import { API_ENDPOINTS, getAuthHeaders } from '@/lib/api';
import { useRouter } from 'next/navigation';
import toast from 'react-hot-toast';

interface Dataset {
  uid: string;
  id?: string;
  filename: string;
  created_at: string;
  parsed_ok: boolean;
  row_count: number;
}

interface ChartSpec {
  uid: string;
  chart_type: string;
  created_at: string;
  is_canonical: boolean;
}

interface DatasetWithCharts extends Dataset {
  charts?: ChartSpec[];
  chartCount?: number;
}

export default function ChartsPage() {
  const [datasets, setDatasets] = useState<DatasetWithCharts[]>([]);
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState<string | null>(null);
  const [deleting, setDeleting] = useState<string | null>(null);
  const [deletingAll, setDeletingAll] = useState(false);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [deleteAllDialogOpen, setDeleteAllDialogOpen] = useState(false);
  const [datasetToDelete, setDatasetToDelete] = useState<{ uid: string; filename: string } | null>(null);
  const router = useRouter();

  useEffect(() => {
    fetchDatasets();
  }, []);

  const fetchDatasets = async () => {
    try {
      // Fetch datasets
      const datasetsResponse = await axios.get(API_ENDPOINTS.datasets.list, {
        headers: getAuthHeaders(),
      });
      const datasetsData = datasetsResponse.data.results || datasetsResponse.data;
      
      // Fetch chart summary (counts only, not full data)
      const summaryResponse = await axios.get(API_ENDPOINTS.charts.summary, {
        headers: getAuthHeaders(),
      });
      const chartSummary = summaryResponse.data.results || [];
      
      // Create a map for quick lookup
      const summaryMap = new Map(
        chartSummary.map((s: { dataset_uid: string; chart_count: number }) => [s.dataset_uid, s.chart_count])
      );
      
      // Merge datasets with chart counts
      const datasetsWithCharts = datasetsData.map((dataset: Dataset) => ({
        ...dataset,
        chartCount: summaryMap.get(dataset.uid) || 0,
      }));
      
      setDatasets(datasetsWithCharts);
    } catch (error) {
      console.error('Failed to fetch datasets:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleGenerateChart = async (datasetUid: string) => {
    try {
      setGenerating(datasetUid);
      
      const response = await axios.post(
        API_ENDPOINTS.charts.generate,
        { dataset_id: datasetUid },
        { headers: getAuthHeaders() }
      );

      const { charts_created, is_taam } = response.data;
      
      toast.success(
        `Generated ${charts_created} chart${charts_created !== 1 ? 's' : ''} • ${is_taam ? 'TAAM Analysis' : 'Generic Charts'}`,
        {
          icon: '📊',
        }
      );
      
      // Refresh the datasets to show new charts
      await fetchDatasets();
      
    } catch (error) {
      const err = error as { response?: { data?: { error?: string } } };
      toast.error(err.response?.data?.error || 'Failed to generate chart');
    } finally {
      setGenerating(null);
    }
  };

  const handleViewCharts = (datasetUid: string) => {
    router.push(`/dashboard/charts/${datasetUid}`);
  };

  const handleDeleteClick = (datasetUid: string, filename: string) => {
    setDatasetToDelete({ uid: datasetUid, filename });
    setDeleteDialogOpen(true);
  };

  const handleDeleteConfirm = async () => {
    if (!datasetToDelete) return;
    
    try {
      setDeleting(datasetToDelete.uid);
      
      await axios.delete(
        API_ENDPOINTS.datasets.detail(datasetToDelete.uid),
        { headers: getAuthHeaders() }
      );
      
      // Remove from local state
      setDatasets(datasets.filter(d => d.uid !== datasetToDelete.uid));
      
      // Show success toast
      toast.success(`Successfully deleted "${datasetToDelete.filename}"`, {
        icon: '🗑️',
      });
      
    } catch (error) {
      const err = error as { response?: { data?: { error?: string } } };
      toast.error(err.response?.data?.error || 'Failed to delete dataset');
    } finally {
      setDeleting(null);
      setDeleteDialogOpen(false);
      setDatasetToDelete(null);
    }
  };

  const handleDeleteAllConfirm = async () => {
    try {
      setDeletingAll(true);
      
      const deletePromises = datasets.map(dataset =>
        axios.delete(
          API_ENDPOINTS.datasets.detail(dataset.uid),
          { headers: getAuthHeaders() }
        )
      );
      
      await Promise.all(deletePromises);
      
      // Clear all datasets
      setDatasets([]);
      
      // Show success toast
      toast.success('Successfully deleted all datasets', {
        icon: '🗑️',
      });
      
    } catch (error) {
      const err = error as { response?: { data?: { error?: string } } };
      toast.error(err.response?.data?.error || 'Failed to delete some datasets');
    } finally {
      setDeletingAll(false);
      setDeleteAllDialogOpen(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader2 className="h-8 w-8 animate-spin text-blue-600" />
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto">
      <div className="flex items-center justify-between mb-2">
        <h1 className="text-3xl font-bold text-gray-900">Charts</h1>
        {datasets.length > 0 && (
          <Button
            onClick={() => setDeleteAllDialogOpen(true)}
            disabled={deletingAll}
            variant="destructive"
          >
            {deletingAll ? (
              <>
                <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                Deleting All...
              </>
            ) : (
              <>
                <Trash2 className="h-4 w-4 mr-2" />
                Delete All
              </>
            )}
          </Button>
        )}
      </div>
      <p className="text-gray-600 mb-8">
        Generate and view charts from your uploaded datasets
      </p>

      {datasets.length === 0 ? (
        <Card className="p-12 text-center">
          <BarChart3 className="h-12 w-12 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">
            No datasets uploaded yet
          </h3>
          <p className="text-gray-600 mb-6">
            Upload a CSV or XLSX file to get started with chart generation
          </p>
          <Button onClick={() => (window.location.href = '/dashboard/upload')}>
            Upload Data
          </Button>
        </Card>
      ) : (
        <div className="space-y-4">
          {datasets.map((dataset) => (
            <Card key={dataset.uid} className="p-6">
              <div className="flex items-center justify-between">
                <div className="flex-1">
                  <h3 className="font-semibold text-gray-900 mb-1">
                    {dataset.filename}
                  </h3>
                  <div className="flex items-center gap-4 text-sm text-gray-600">
                    <span>{dataset.row_count} rows</span>
                    <span>•</span>
                    <span>
                      {new Date(dataset.created_at).toLocaleDateString()}
                    </span>
                    <span>•</span>
                    <span
                      className={
                        dataset.parsed_ok
                          ? 'text-green-600'
                          : 'text-red-600'
                      }
                    >
                      {dataset.parsed_ok ? 'Parsed successfully' : 'Parse error'}
                    </span>
                    {dataset.chartCount !== undefined && dataset.chartCount > 0 && (
                      <>
                        <span>•</span>
                        <span className="text-blue-600 font-medium">
                          {dataset.chartCount} chart{dataset.chartCount !== 1 ? 's' : ''} generated
                        </span>
                      </>
                    )}
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  {dataset.chartCount && dataset.chartCount > 0 ? (
                    <>
                      <Button
                        onClick={() => handleViewCharts(dataset.uid)}
                        variant="default"
                      >
                        <Eye className="h-4 w-4 mr-2" />
                        View Charts
                      </Button>
                      <Button
                        onClick={() => handleDeleteClick(dataset.uid, dataset.filename)}
                        disabled={deleting === dataset.uid}
                        variant="destructive"
                      >
                        {deleting === dataset.uid ? (
                          <>
                            <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                            Deleting...
                          </>
                        ) : (
                          <>
                            <Trash2 className="h-4 w-4 mr-2" />
                            Delete
                          </>
                        )}
                      </Button>
                    </>
                  ) : (
                    <>
                      <Button
                        onClick={() => handleGenerateChart(dataset.uid)}
                        disabled={!dataset.parsed_ok || generating === dataset.uid}
                      >
                        {generating === dataset.uid ? (
                          <>
                            <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                            Generating...
                          </>
                        ) : (
                          <>
                            <BarChart3 className="h-4 w-4 mr-2" />
                            Generate Charts
                          </>
                        )}
                      </Button>
                      <Button
                        onClick={() => handleDeleteClick(dataset.uid, dataset.filename)}
                        disabled={deleting === dataset.uid}
                        variant="destructive"
                      >
                        {deleting === dataset.uid ? (
                          <>
                            <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                            Deleting...
                          </>
                        ) : (
                          <>
                            <Trash2 className="h-4 w-4 mr-2" />
                            Delete
                          </>
                        )}
                      </Button>
                    </>
                  )}
                </div>
              </div>
            </Card>
          ))}
        </div>
      )}

      {/* Delete Confirmation Dialog */}
      <DeleteConfirmationDialog
        isOpen={deleteDialogOpen}
        onClose={() => setDeleteDialogOpen(false)}
        onConfirm={handleDeleteConfirm}
        title="Delete Dataset"
        description="This will permanently delete the dataset and all associated charts. This action cannot be undone."
        itemName={datasetToDelete?.filename || ''}
      />

      {/* Delete All Confirmation Dialog */}
      <DeleteAllConfirmationDialog
        isOpen={deleteAllDialogOpen}
        onClose={() => setDeleteAllDialogOpen(false)}
        onConfirm={handleDeleteAllConfirm}
        itemCount={datasets.length}
      />
    </div>
  );
}
