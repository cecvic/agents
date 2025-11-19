/**
 * Main Dashboard Page
 *
 * Shows overview of all migrations with create and manage functionality
 */

import { useState } from 'react';
import Head from 'next/head';
import { useRouter } from 'next/router';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Plus, ArrowRight, CheckCircle, XCircle, Clock, Loader } from 'lucide-react';
import { format } from 'date-fns';
import toast from 'react-hot-toast';
import { migrationApi } from '@/lib/api';
import { Migration, MigrationStatus } from '@/types';

export default function Dashboard() {
  const router = useRouter();
  const queryClient = useQueryClient();
  const [showCreateModal, setShowCreateModal] = useState(false);

  // Fetch migrations
  const { data: migrations, isLoading } = useQuery({
    queryKey: ['migrations'],
    queryFn: () => migrationApi.listMigrations(),
    refetchInterval: 5000, // Refresh every 5 seconds
  });

  const handleViewMigration = (migrationId: string) => {
    router.push(`/migrations/${migrationId}`);
  };

  const getStatusIcon = (status: MigrationStatus) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="w-5 h-5 text-green-500" />;
      case 'failed':
        return <XCircle className="w-5 h-5 text-red-500" />;
      case 'pending':
      case 'extracting':
      case 'analyzing':
      case 'converting':
      case 'validating':
        return <Loader className="w-5 h-5 text-blue-500 animate-spin" />;
      default:
        return <Clock className="w-5 h-5 text-gray-400" />;
    }
  };

  const getStatusColor = (status: MigrationStatus) => {
    switch (status) {
      case 'completed':
        return 'bg-green-100 text-green-800';
      case 'failed':
        return 'bg-red-100 text-red-800';
      case 'pending':
        return 'bg-gray-100 text-gray-800';
      default:
        return 'bg-blue-100 text-blue-800';
    }
  };

  const getStatusText = (status: MigrationStatus) => {
    return status.charAt(0).toUpperCase() + status.slice(1).replace('_', ' ');
  };

  return (
    <>
      <Head>
        <title>Dashboard - Website Migration Platform</title>
        <meta name="description" content="Manage your website migrations" />
      </Head>

      <div className="min-h-screen bg-gray-50">
        {/* Header */}
        <header className="bg-white border-b border-gray-200">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
            <div className="flex justify-between items-center">
              <div>
                <h1 className="text-3xl font-bold text-gray-900">
                  Migration Dashboard
                </h1>
                <p className="mt-1 text-sm text-gray-500">
                  Manage and monitor your website migrations
                </p>
              </div>
              <button
                onClick={() => router.push('/migrations/new')}
                className="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
              >
                <Plus className="w-5 h-5 mr-2" />
                New Migration
              </button>
            </div>
          </div>
        </header>

        {/* Main Content */}
        <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          {/* Stats */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
            <StatCard
              title="Total Migrations"
              value={migrations?.length || 0}
              icon="📊"
            />
            <StatCard
              title="Completed"
              value={migrations?.filter((m) => m.status === 'completed').length || 0}
              icon="✅"
            />
            <StatCard
              title="In Progress"
              value={
                migrations?.filter((m) =>
                  ['extracting', 'analyzing', 'converting', 'validating'].includes(m.status)
                ).length || 0
              }
              icon="⏳"
            />
            <StatCard
              title="Avg. Similarity"
              value={
                migrations?.filter((m) => m.similarity_score)
                  .reduce((acc, m) => acc + (m.similarity_score || 0), 0) /
                  (migrations?.filter((m) => m.similarity_score).length || 1) || 0
              }
              format={(v) => `${(v * 100).toFixed(0)}%`}
              icon="🎯"
            />
          </div>

          {/* Migrations List */}
          <div className="bg-white shadow-sm rounded-lg overflow-hidden">
            <div className="px-6 py-4 border-b border-gray-200">
              <h2 className="text-lg font-semibold text-gray-900">Recent Migrations</h2>
            </div>

            {isLoading ? (
              <div className="flex items-center justify-center py-12">
                <Loader className="w-8 h-8 text-blue-500 animate-spin" />
              </div>
            ) : migrations && migrations.length > 0 ? (
              <div className="divide-y divide-gray-200">
                {migrations.map((migration) => (
                  <MigrationRow
                    key={migration.id}
                    migration={migration}
                    onClick={() => handleViewMigration(migration.id)}
                    getStatusIcon={getStatusIcon}
                    getStatusColor={getStatusColor}
                    getStatusText={getStatusText}
                  />
                ))}
              </div>
            ) : (
              <div className="text-center py-12">
                <p className="text-gray-500 mb-4">No migrations yet</p>
                <button
                  onClick={() => router.push('/migrations/new')}
                  className="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700"
                >
                  <Plus className="w-5 h-5 mr-2" />
                  Create Your First Migration
                </button>
              </div>
            )}
          </div>
        </main>
      </div>
    </>
  );
}

function StatCard({ title, value, icon, format }: any) {
  const displayValue = format ? format(value) : value;

  return (
    <div className="bg-white rounded-lg shadow-sm p-6">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm font-medium text-gray-600">{title}</p>
          <p className="mt-2 text-3xl font-bold text-gray-900">{displayValue}</p>
        </div>
        <div className="text-4xl">{icon}</div>
      </div>
    </div>
  );
}

function MigrationRow({ migration, onClick, getStatusIcon, getStatusColor, getStatusText }: any) {
  return (
    <div
      className="px-6 py-4 hover:bg-gray-50 cursor-pointer transition-colors"
      onClick={onClick}
    >
      <div className="flex items-center justify-between">
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-3 mb-2">
            {getStatusIcon(migration.status)}
            <h3 className="text-lg font-semibold text-gray-900 truncate">
              {migration.project_name}
            </h3>
          </div>

          <div className="flex items-center gap-4 text-sm text-gray-500">
            <span>From: {migration.source_platform}</span>
            <span>→</span>
            <span>To: {migration.target_platform}</span>
            <span>•</span>
            <span>{format(new Date(migration.created_at), 'MMM dd, yyyy')}</span>
          </div>

          {migration.current_step && (
            <div className="mt-2">
              <p className="text-sm text-gray-600">{migration.current_step}</p>
              {migration.progress > 0 && (
                <div className="mt-1 w-64 bg-gray-200 rounded-full h-2">
                  <div
                    className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                    style={{ width: `${migration.progress * 100}%` }}
                  />
                </div>
              )}
            </div>
          )}
        </div>

        <div className="flex items-center gap-4">
          {migration.similarity_score && (
            <div className="text-center">
              <p className="text-2xl font-bold text-gray-900">
                {(migration.similarity_score * 100).toFixed(0)}%
              </p>
              <p className="text-xs text-gray-500">Similarity</p>
            </div>
          )}

          <span
            className={`inline-flex items-center px-3 py-1 rounded-full text-xs font-medium ${getStatusColor(
              migration.status
            )}`}
          >
            {getStatusText(migration.status)}
          </span>

          <ArrowRight className="w-5 h-5 text-gray-400" />
        </div>
      </div>
    </div>
  );
}
