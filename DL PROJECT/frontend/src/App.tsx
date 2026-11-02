import React, { useState, useEffect } from 'react';
import { Sidebar } from './components/Sidebar';
import { Header } from './components/Header';
import { DashboardPage } from './pages/DashboardPage';
import { SummarizeTextPage } from './pages/SummarizeTextPage';
import { SummarizePdfPage } from './pages/SummarizePdfPage';
import { ModelComparisonPage } from './pages/ModelComparisonPage';
import { EvaluationPage } from './pages/EvaluationPage';
import { HistoryPage } from './pages/HistoryPage';
import { SettingsPage } from './pages/SettingsPage';
import { HealthResponse, ModelInfo, LengthProfile } from './types';
import { api } from './services/api';

export const App: React.FC = () => {
  const [currentPage, setCurrentPage] = useState<string>('dashboard');
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [models, setModels] = useState<ModelInfo[]>([]);
  const [lengthProfiles, setLengthProfiles] = useState<Record<string, LengthProfile>>({});
  const [isCheckingHealth, setIsCheckingHealth] = useState<boolean>(false);

  useEffect(() => {
    fetchInitialData();
  }, []);

  const fetchInitialData = async () => {
    setIsCheckingHealth(true);
    try {
      const healthData = await api.checkHealth();
      setHealth(healthData);
      const modelsData = await api.getModels();
      setModels(modelsData.models);
      setLengthProfiles(modelsData.length_profiles);
    } catch (err) {
      console.error('Failed to connect to FastAPI backend:', err);
    } finally {
      setIsCheckingHealth(false);
    }
  };

  const getPageTitle = (page: string): string => {
    switch (page) {
      case 'dashboard':
        return 'System Overview & Telemetry';
      case 'summarize-text':
        return 'Text Summarization Workspace';
      case 'summarize-pdf':
        return 'PDF Document Summarization';
      case 'comparison':
        return 'Transformer Model Comparison';
      case 'evaluation':
        return 'Summary Evaluation Metrics';
      case 'history':
        return 'Session History & Archive';
      case 'settings':
        return 'Configuration & Hardware Specs';
      default:
        return 'Neural Summarizer Studio';
    }
  };

  return (
    <div className="flex min-h-screen bg-[#F8FAFC]">
      {/* Sidebar Navigation */}
      <Sidebar
        currentPage={currentPage}
        onSelectPage={setCurrentPage}
        activeDevice={health?.device || 'PyTorch Inference Engine'}
      />

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col min-w-0">
        <Header
          pageTitle={getPageTitle(currentPage)}
          health={health}
          onRefreshHealth={fetchInitialData}
          isChecking={isCheckingHealth}
        />

        <main className="flex-1 p-6 sm:p-8 overflow-y-auto">
          {currentPage === 'dashboard' && (
            <DashboardPage
              onNavigate={setCurrentPage}
              models={models}
              device={health?.device || 'PyTorch (CPU/GPU)'}
            />
          )}

          {currentPage === 'summarize-text' && (
            <SummarizeTextPage
              models={models}
              lengthProfiles={lengthProfiles}
              onNavigate={setCurrentPage}
            />
          )}

          {currentPage === 'summarize-pdf' && <SummarizePdfPage />}

          {currentPage === 'comparison' && <ModelComparisonPage />}

          {currentPage === 'evaluation' && <EvaluationPage />}

          {currentPage === 'history' && <HistoryPage />}

          {currentPage === 'settings' && (
            <SettingsPage
              health={health}
              onRefreshHealth={fetchInitialData}
            />
          )}
        </main>
      </div>
    </div>
  );
};

export default App;
