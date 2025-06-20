import React, { useState } from 'react';
import { Container, Tabs, Tab, Box, Typography, TextField, Button, Paper, CircularProgress, Alert, IconButton, Tooltip } from '@mui/material';
import ContentCopyIcon from '@mui/icons-material/ContentCopy';
import { scrapeBlogGuide, getScrapeStatus, getScrapeResults, scrapePdf } from './api';

// Type definitions
interface TabPanelProps {
  children?: React.ReactNode;
  value: number;
  index: number;
}

// interface ScrapeSource {
//   type: string;
//   url: string;
//   selectors?: string[];
// }

// interface ScrapeRequest {
//   team_id: string;
//   user_id: string;
//   sources: ScrapeSource[];
// }

interface ScrapeResponse {
  job_id: string;
  status: string;
  message?: string;
}

interface StatusResponse {
  job_id: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  progress?: number;
  message?: string;
}

interface ScrapeResult {
  title: string;
  url: string;
  content: string;
  timestamp?: string;
}

interface ResultsResponse {
  job_id: string;
  status: string;
  results: ScrapeResult[];
  total_results: number;
}

interface PdfResponse {
  filename: string;
  chunks: string[];
  total_chunks: number;
  metadata?: Record<string, unknown>;
}

interface ApiError {
  response?: {
    data?: {
      detail?: string;
    };
  };
  message: string;
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props;
  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`tabpanel-${index}`}
      aria-labelledby={`tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
    </div>
  );
}

const App: React.FC = () => {
  const [tab, setTab] = useState(0);
  
  // Scrape Blog/Guide
  const [scrapeUrl, setScrapeUrl] = useState('https://interviewing.io/blog');
  const [scrapeSelectors, setScrapeSelectors] = useState('');
  const [scrapeLoading, setScrapeLoading] = useState(false);
  const [scrapeResult, setScrapeResult] = useState<ScrapeResponse | null>(null);
  const [scrapeError, setScrapeError] = useState<string | null>(null);
  const [copySuccess, setCopySuccess] = useState(false);
  
  // Status
  const [statusJobId, setStatusJobId] = useState('');
  const [statusLoading, setStatusLoading] = useState(false);
  const [statusResult, setStatusResult] = useState<StatusResponse | null>(null);
  const [statusError, setStatusError] = useState<string | null>(null);
  
  // Results
  const [resultsJobId, setResultsJobId] = useState('');
  const [resultsLoading, setResultsLoading] = useState(false);
  const [resultsResult, setResultsResult] = useState<ResultsResponse | null>(null);
  const [resultsError, setResultsError] = useState<string | null>(null);
  
  // PDF
  const [pdfFile, setPdfFile] = useState<File | null>(null);
  const [pdfLoading, setPdfLoading] = useState(false);
  const [pdfResult, setPdfResult] = useState<PdfResponse | null>(null);
  const [pdfError, setPdfError] = useState<string | null>(null);

  // Copy to clipboard handler
  const handleCopyJobId = async (jobId: string) => {
    try {
      await navigator.clipboard.writeText(jobId);
      setCopySuccess(true);
      setTimeout(() => setCopySuccess(false), 2000);
    } catch (err) {
      console.error('Failed to copy:', err);
    }
  };

  // Handlers
  const handleScrape = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setScrapeLoading(true);
    setScrapeError(null);
    setScrapeResult(null);
    try {
      // Fix: convert ScrapeRequest to a plain object for API call
      const data = {
        team_id: "demo-team",
        user_id: "demo-user",
        sources: [
          {
            type: "blog",
            url: scrapeUrl,
            ...(scrapeSelectors && { selectors: scrapeSelectors.split(',').map(s => s.trim()) })
          }
        ]
      };
      const res = await scrapeBlogGuide(data);
      setScrapeResult(res.data as ScrapeResponse);
    } catch (err) {
      const error = err as ApiError;
      setScrapeError(error?.response?.data?.detail || error.message);
    } finally {
      setScrapeLoading(false);
    }
  };

  const handleStatus = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setStatusLoading(true);
    setStatusError(null);
    setStatusResult(null);
    try {
      const res = await getScrapeStatus(statusJobId);
      setStatusResult(res.data as StatusResponse);
    } catch (err) {
      const error = err as ApiError;
      setStatusError(error?.response?.data?.detail || error.message);
    } finally {
      setStatusLoading(false);
    }
  };

  const handleResults = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setResultsLoading(true);
    setResultsError(null);
    setResultsResult(null);
    try {
      const res = await getScrapeResults(resultsJobId);
      setResultsResult(res.data as ResultsResponse);
    } catch (err) {
      const error = err as ApiError;
      setResultsError(error?.response?.data?.detail || error.message);
    } finally {
      setResultsLoading(false);
    }
  };

  const handlePdf = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    if (!pdfFile) {
      setPdfError('Please select a PDF file.');
      return;
    }
    setPdfLoading(true);
    setPdfError(null);
    setPdfResult(null);
    try {
      const formData = new FormData();
      formData.append('file', pdfFile);
      const res = await scrapePdf(formData);
      setPdfResult(res.data as PdfResponse);
    } catch (err) {
      const error = err as ApiError;
      setPdfError(error?.response?.data?.detail || error.message);
    } finally {
      setPdfLoading(false);
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (files && files.length > 0) {
      setPdfFile(files[0]);
    } else {
      setPdfFile(null);
    }
  };

  return (
    <Container maxWidth="md" sx={{ mt: 4 }}>
      <Paper elevation={3} sx={{ p: 2, mb: 2 }}>
        <Typography variant="h4" gutterBottom>Aline Scraper Frontend</Typography>
        <Typography variant="body1" gutterBottom>
          Use the tabs below to interact with the API. Each form has instructions and example values.
        </Typography>
      </Paper>
      <Tabs value={tab} onChange={(_event: React.SyntheticEvent, v: number) => setTab(v)} centered>
        <Tab label="Scrape Blog/Guide" />
        <Tab label="Scrape Status" />
        <Tab label="Scrape Results" />
        <Tab label="PDF Scraper" />
      </Tabs>
      
      {/* Scrape Blog/Guide */}
      <TabPanel value={tab} index={0}>
        <Typography variant="h6">Scrape Blog/Guide</Typography>
        <Typography variant="body2" gutterBottom>
          Enter a blog or guide index URL. Optionally, provide custom selectors (JSON or comma-separated).<br />
          Example: <code>https://interviewing.io/blog</code>
        </Typography>
        <Box component="form" onSubmit={handleScrape} sx={{ mt: 2 }}>
          <TextField
            label="Index URL"
            value={scrapeUrl}
            onChange={e => setScrapeUrl(e.target.value)}
            fullWidth
            required
            sx={{ mb: 2 }}
          />
          <TextField
            label="Selectors (optional)"
            value={scrapeSelectors}
            onChange={e => setScrapeSelectors(e.target.value)}
            fullWidth
            sx={{ mb: 2 }}
            helperText="Custom CSS selectors as JSON or comma-separated. Leave blank for auto-detect."
          />
          <Button type="submit" variant="contained" disabled={scrapeLoading}>
            {scrapeLoading ? <CircularProgress size={24} /> : 'Start Scrape'}
          </Button>
        </Box>
        {scrapeError && <Alert severity="error" sx={{ mt: 2 }}>{scrapeError}</Alert>}
        {scrapeResult && (
          <Paper sx={{ mt: 2, p: 2 }}>
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
              <Typography variant="subtitle2" sx={{ mr: 1 }}>Job ID:</Typography>
              <Typography variant="body2" sx={{ fontFamily: 'monospace', mr: 1 }}>
                {scrapeResult.job_id}
              </Typography>
              <Tooltip title={copySuccess ? "Copied!" : "Copy Job ID"}>
                <IconButton
                  size="small"
                  onClick={() => handleCopyJobId(scrapeResult.job_id)}
                  sx={{ ml: 'auto' }}
                >
                  <ContentCopyIcon fontSize="small" />
                </IconButton>
              </Tooltip>
            </Box>
            <Paper sx={{ p: 2, whiteSpace: 'pre-wrap', maxHeight: 300, overflow: 'auto', bgcolor: 'grey.50' }}>
              <Typography variant="subtitle2">Full Response:</Typography>
              <code>{JSON.stringify(scrapeResult, null, 2)}</code>
            </Paper>
          </Paper>
        )}
      </TabPanel>
      
      {/* Scrape Status */}
      <TabPanel value={tab} index={1}>
        <Typography variant="h6">Scrape Status</Typography>
        <Typography variant="body2" gutterBottom>
          Enter a job ID to check the status of a scrape job.<br />
          Example: <code>123e4567-e89b-12d3-a456-426614174000</code>
        </Typography>
        <Box component="form" onSubmit={handleStatus} sx={{ mt: 2 }}>
          <TextField
            label="Job ID"
            value={statusJobId}
            onChange={e => setStatusJobId(e.target.value)}
            fullWidth
            required
            sx={{ mb: 2 }}
          />
          <Button type="submit" variant="contained" disabled={statusLoading}>
            {statusLoading ? <CircularProgress size={24} /> : 'Check Status'}
          </Button>
        </Box>
        {statusError && <Alert severity="error" sx={{ mt: 2 }}>{statusError}</Alert>}
        {statusResult && (
          <Paper sx={{ mt: 2, p: 2, whiteSpace: 'pre-wrap', maxHeight: 300, overflow: 'auto' }}>
            <Typography variant="subtitle2">Response:</Typography>
            <code>{JSON.stringify(statusResult, null, 2)}</code>
          </Paper>
        )}
      </TabPanel>
      
      {/* Scrape Results */}
      <TabPanel value={tab} index={2}>
        <Typography variant="h6">Scrape Results</Typography>
        <Typography variant="body2" gutterBottom>
          Enter a job ID to fetch the results of a completed scrape job.<br />
          Example: <code>123e4567-e89b-12d3-a456-426614174000</code>
        </Typography>
        <Box component="form" onSubmit={handleResults} sx={{ mt: 2 }}>
          <TextField
            label="Job ID"
            value={resultsJobId}
            onChange={e => setResultsJobId(e.target.value)}
            fullWidth
            required
            sx={{ mb: 2 }}
          />
          <Button type="submit" variant="contained" disabled={resultsLoading}>
            {resultsLoading ? <CircularProgress size={24} /> : 'Get Results'}
          </Button>
        </Box>
        {resultsError && <Alert severity="error" sx={{ mt: 2 }}>{resultsError}</Alert>}
        {resultsResult && (
          <Paper sx={{ mt: 2, p: 2, whiteSpace: 'pre-wrap', maxHeight: 300, overflow: 'auto' }}>
            <Typography variant="subtitle2">Response:</Typography>
            <code>{JSON.stringify(resultsResult, null, 2)}</code>
          </Paper>
        )}
      </TabPanel>
      
      {/* PDF Scraper */}
      <TabPanel value={tab} index={3}>
        <Typography variant="h6">PDF Scraper</Typography>
        <Typography variant="body2" gutterBottom>
          Upload a PDF file to extract and chunk its content.
        </Typography>
        <Box component="form" onSubmit={handlePdf} sx={{ mt: 2 }}>
          <Button variant="contained" component="label" sx={{ mb: 2 }}>
            Select PDF
            <input
              type="file"
              accept="application/pdf"
              hidden
              onChange={handleFileChange}
            />
          </Button>
          {pdfFile && <Typography variant="body2">Selected: {pdfFile.name}</Typography>}
          <br />
          <Button type="submit" variant="contained" disabled={pdfLoading} sx={{ mt: 1 }}>
            {pdfLoading ? <CircularProgress size={24} /> : 'Extract PDF'}
          </Button>
        </Box>
        {pdfError && <Alert severity="error" sx={{ mt: 2 }}>{pdfError}</Alert>}
        {pdfResult && (
          <Paper sx={{ mt: 2, p: 2, whiteSpace: 'pre-wrap', maxHeight: 300, overflow: 'auto' }}>
            <Typography variant="subtitle2">Response:</Typography>
            <code>{JSON.stringify(pdfResult, null, 2)}</code>
          </Paper>
        )}
      </TabPanel>
    </Container>
  );
};

export default App;