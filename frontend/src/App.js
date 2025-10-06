import { useState, useEffect } from "react";
import "./App.css";
import axios from "axios";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || "http://localhost:8000";
const API = `${BACKEND_URL}/api`;
const MCP_API = `${BACKEND_URL}/mcp/api/v1`;

function App() {
  const [tools, setTools] = useState([]);
  const [selectedTool, setSelectedTool] = useState(null);
  const [parameters, setParameters] = useState({});
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState("mcp-tools");
  const [context, setContext] = useState({});
  const [files, setFiles] = useState([]);
  const [streaming, setStreaming] = useState(false);

  useEffect(() => {
    fetchTools();
    fetchContext();
    fetchFiles();
  }, []);

  const fetchTools = async () => {
    try {
      const response = await axios.get(`${API}/tools`);
      setTools(response.data.tools);
    } catch (e) {
      console.error("Error fetching tools:", e);
      setError("Failed to fetch MCP tools");
    }
  };

  const fetchContext = async () => {
    try {
      const response = await axios.get(`${MCP_API}/context`);
      setContext(response.data);
    } catch (e) {
      console.error("Error fetching context:", e);
    }
  };

  const fetchFiles = async () => {
    try {
      const response = await axios.get(`${MCP_API}/files`);
      setFiles(response.data.files || []);
    } catch (e) {
      console.error("Error fetching files:", e);
    }
  };

  const handleToolSelect = (tool) => {
    setSelectedTool(tool);
    setParameters({});
    setResult(null);
    setError(null);
  };

  const handleParameterChange = (paramName, value) => {
    setParameters(prev => ({
      ...prev,
      [paramName]: value
    }));
  };

  const executeTool = async () => {
    if (!selectedTool) return;

    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const response = await axios.post(`${API}/execute`, {
        tool_name: selectedTool.name,
        arguments: parameters
      });

      if (response.data.success) {
        setResult(response.data.result);
      } else {
        setError(response.data.error || "Tool execution failed");
      }
    } catch (e) {
      console.error("Error executing tool:", e);
      setError(e.response?.data?.detail || "Failed to execute tool");
    } finally {
      setLoading(false);
    }
  };

  const renderParameterInput = (paramName, paramInfo) => {
    const isTextarea = paramName === 'content';
    const commonClasses = "w-full px-4 py-3 rounded-lg border border-gray-300 focus:border-indigo-500 focus:ring-2 focus:ring-indigo-200 outline-none transition-all";

    return (
      <div key={paramName} className="space-y-2">
        <label className="block text-sm font-medium text-gray-700">
          {paramName.split('_').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ')}
          {paramInfo.required && <span className="text-red-500 ml-1">*</span>}
        </label>
        {isTextarea ? (
          <textarea
            value={parameters[paramName] || ''}
            onChange={(e) => handleParameterChange(paramName, e.target.value)}
            placeholder={paramInfo.description}
            rows={6}
            className={commonClasses}
          />
        ) : (
          <input
            type="text"
            value={parameters[paramName] || ''}
            onChange={(e) => handleParameterChange(paramName, e.target.value)}
            placeholder={paramInfo.description}
            className={commonClasses}
          />
        )}
        <p className="text-xs text-gray-500">{paramInfo.description}</p>
      </div>
    );
  };

  const renderResult = () => {
    if (!result) return null;

    let displayResult = result;
    let isJson = false;

    if (typeof result === 'object') {
      displayResult = JSON.stringify(result, null, 2);
      isJson = true;
    }

    return (
      <div className="mt-6 bg-gradient-to-br from-green-50 to-emerald-50 rounded-xl p-6 border border-green-200">
        <div className="flex items-center gap-2 mb-4">
          <svg className="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <h3 className="text-lg font-semibold text-gray-800">Result</h3>
        </div>
        <pre className="bg-white rounded-lg p-4 overflow-x-auto text-sm border border-green-200">
          <code className={isJson ? "text-gray-800" : "text-gray-700"}>{displayResult}</code>
        </pre>
      </div>
    );
  };

  const renderMCPTools = () => (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
      {/* Tools List */}
      <div className="lg:col-span-1">
        <div className="bg-white rounded-2xl shadow-lg border border-gray-200 overflow-hidden">
          <div className="bg-gradient-to-r from-indigo-500 to-purple-600 px-6 py-4">
            <h2 className="text-xl font-bold text-white flex items-center gap-2">
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
              </svg>
              MCP Tools
            </h2>
          </div>
          <div className="p-4 space-y-2">
            {tools.length === 0 ? (
              <p className="text-gray-500 text-center py-8">Loading tools...</p>
            ) : (
              tools.map((tool) => (
                <button
                  key={tool.name}
                  onClick={() => handleToolSelect(tool)}
                  className={`w-full text-left px-4 py-4 rounded-xl transition-all duration-200 ${
                    selectedTool?.name === tool.name
                      ? 'bg-gradient-to-r from-indigo-500 to-purple-600 text-white shadow-lg transform scale-105'
                      : 'bg-gray-50 hover:bg-gray-100 text-gray-800 hover:shadow-md'
                  }`}
                >
                  <div className="font-semibold text-sm mb-1">{tool.name}</div>
                  <div className={`text-xs ${
                    selectedTool?.name === tool.name ? 'text-indigo-100' : 'text-gray-600'
                  }`}>
                    {tool.description}
                  </div>
                </button>
              ))
            )}
          </div>
        </div>
      </div>

      {/* Tool Execution Panel */}
      <div className="lg:col-span-2">
        {!selectedTool ? (
          <div className="bg-white rounded-2xl shadow-lg border border-gray-200 p-12 text-center">
            <div className="inline-block bg-indigo-100 p-6 rounded-full mb-4">
              <svg className="w-16 h-16 text-indigo-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
            </div>
            <h3 className="text-2xl font-bold text-gray-800 mb-2">Select a Tool to Get Started</h3>
            <p className="text-gray-600">Choose a tool from the left panel to execute MCP operations</p>
          </div>
        ) : (
          <div className="bg-white rounded-2xl shadow-lg border border-gray-200 overflow-hidden">
            <div className="bg-gradient-to-r from-purple-500 to-indigo-600 px-6 py-4">
              <h2 className="text-xl font-bold text-white">{selectedTool.name}</h2>
              <p className="text-purple-100 text-sm mt-1">{selectedTool.description}</p>
            </div>

            <div className="p-6">
              {/* Parameters Form */}
              <div className="space-y-5 mb-6">
                {Object.entries(selectedTool.parameters).map(([paramName, paramInfo]) =>
                  renderParameterInput(paramName, paramInfo)
                )}
              </div>

              {/* Execute Button */}
              <button
                onClick={executeTool}
                disabled={loading}
                className="w-full bg-gradient-to-r from-indigo-500 to-purple-600 text-white font-semibold py-4 px-6 rounded-xl hover:from-indigo-600 hover:to-purple-700 focus:outline-none focus:ring-4 focus:ring-indigo-300 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 shadow-lg hover:shadow-xl flex items-center justify-center gap-2"
              >
                {loading ? (
                  <>
                    <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                    </svg>
                    <span>Executing...</span>
                  </>
                ) : (
                  <>
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" />
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    <span>Execute Tool</span>
                  </>
                )}
              </button>

              {/* Error Display */}
              {error && (
                <div className="mt-6 bg-red-50 border border-red-200 rounded-xl p-4">
                  <div className="flex items-start gap-3">
                    <svg className="w-6 h-6 text-red-600 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    <div>
                      <h4 className="font-semibold text-red-800">Error</h4>
                      <p className="text-red-700 text-sm mt-1">{error}</p>
                    </div>
                  </div>
                </div>
              )}

              {/* Result Display */}
              {renderResult()}
            </div>
          </div>
        )}
      </div>
    </div>
  );

  const renderContextManagement = () => (
    <div className="bg-white rounded-2xl shadow-lg border border-gray-200 p-6">
      <h2 className="text-2xl font-bold text-gray-800 mb-6">Context Management</h2>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div>
          <h3 className="text-lg font-semibold text-gray-700 mb-4">Current Context</h3>
          <div className="bg-gray-50 rounded-lg p-4 max-h-64 overflow-y-auto">
            <pre className="text-sm text-gray-600">
              {JSON.stringify(context, null, 2)}
            </pre>
          </div>
        </div>
        <div>
          <h3 className="text-lg font-semibold text-gray-700 mb-4">Context Operations</h3>
          <div className="space-y-3">
            <button className="w-full bg-blue-500 text-white py-2 px-4 rounded-lg hover:bg-blue-600 transition-colors">
              Add Context Item
            </button>
            <button className="w-full bg-green-500 text-white py-2 px-4 rounded-lg hover:bg-green-600 transition-colors">
              Update Context
            </button>
            <button className="w-full bg-red-500 text-white py-2 px-4 rounded-lg hover:bg-red-600 transition-colors">
              Clear Context
            </button>
          </div>
        </div>
      </div>
    </div>
  );

  const renderFileManagement = () => (
    <div className="bg-white rounded-2xl shadow-lg border border-gray-200 p-6">
      <h2 className="text-2xl font-bold text-gray-800 mb-6">File Management</h2>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div>
          <h3 className="text-lg font-semibold text-gray-700 mb-4">Upload Files</h3>
          <div className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center">
            <svg className="w-12 h-12 text-gray-400 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
            </svg>
            <p className="text-gray-600">Drag and drop files here or click to browse</p>
          </div>
        </div>
        <div>
          <h3 className="text-lg font-semibold text-gray-700 mb-4">File List</h3>
          <div className="bg-gray-50 rounded-lg p-4 max-h-64 overflow-y-auto">
            {files.length === 0 ? (
              <p className="text-gray-500 text-center">No files uploaded</p>
            ) : (
              <div className="space-y-2">
                {files.map((file, index) => (
                  <div key={index} className="flex items-center justify-between bg-white p-2 rounded border">
                    <span className="text-sm text-gray-600">{file.name}</span>
                    <button className="text-red-500 hover:text-red-700 text-sm">Delete</button>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );

  const renderRealTimeStreaming = () => (
    <div className="bg-white rounded-2xl shadow-lg border border-gray-200 p-6">
      <h2 className="text-2xl font-bold text-gray-800 mb-6">Real-time Streaming</h2>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div>
          <h3 className="text-lg font-semibold text-gray-700 mb-4">Stream Controls</h3>
          <div className="space-y-3">
            <button 
              onClick={() => setStreaming(!streaming)}
              className={`w-full py-2 px-4 rounded-lg transition-colors ${
                streaming 
                  ? 'bg-red-500 text-white hover:bg-red-600' 
                  : 'bg-green-500 text-white hover:bg-green-600'
              }`}
            >
              {streaming ? 'Stop Streaming' : 'Start Streaming'}
            </button>
            <div className="flex items-center gap-2">
              <div className={`w-3 h-3 rounded-full ${streaming ? 'bg-green-500' : 'bg-gray-400'}`}></div>
              <span className="text-sm text-gray-600">
                {streaming ? 'Streaming Active' : 'Streaming Inactive'}
              </span>
            </div>
          </div>
        </div>
        <div>
          <h3 className="text-lg font-semibold text-gray-700 mb-4">Stream Events</h3>
          <div className="bg-gray-50 rounded-lg p-4 max-h-64 overflow-y-auto">
            <div className="space-y-2">
              <div className="text-sm text-gray-600">Context updated: user_preferences</div>
              <div className="text-sm text-gray-600">File uploaded: document.pdf</div>
              <div className="text-sm text-gray-600">Tool executed: read_file</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-white to-purple-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200 shadow-sm">
        <div className="max-w-7xl mx-auto px-6 py-6">
          <div className="flex items-center gap-4">
            <div className="bg-gradient-to-br from-indigo-500 to-purple-600 p-3 rounded-xl shadow-lg">
              <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 9l3 3-3 3m5 0h3M5 20h14a2 2 0 002-2V6a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
              </svg>
            </div>
            <div>
              <h1 className="text-3xl font-bold bg-gradient-to-r from-indigo-600 to-purple-600 bg-clip-text text-transparent">
                NEW MCP Server
              </h1>
              <p className="text-gray-600 mt-1">Unified Model Context Protocol - Advanced Features</p>
            </div>
          </div>
        </div>
      </div>

      {/* Navigation Tabs */}
      <div className="max-w-7xl mx-auto px-6 py-4">
        <div className="flex space-x-1 bg-gray-100 rounded-lg p-1">
          {[
            { id: "mcp-tools", label: "MCP Tools", icon: "🔧" },
            { id: "context", label: "Context", icon: "📝" },
            { id: "files", label: "Files", icon: "📁" },
            { id: "streaming", label: "Streaming", icon: "📡" }
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex-1 flex items-center justify-center gap-2 py-2 px-4 rounded-md transition-all ${
                activeTab === tab.id
                  ? 'bg-white text-indigo-600 shadow-sm'
                  : 'text-gray-600 hover:text-gray-800'
              }`}
            >
              <span>{tab.icon}</span>
              <span className="font-medium">{tab.label}</span>
            </button>
          ))}
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-6 pb-8">
        {activeTab === "mcp-tools" && renderMCPTools()}
        {activeTab === "context" && renderContextManagement()}
        {activeTab === "files" && renderFileManagement()}
        {activeTab === "streaming" && renderRealTimeStreaming()}
      </div>

      {/* Footer Info */}
      <div className="mt-8 text-center text-gray-600 text-sm pb-8">
        <p>NEW MCP Server v2.0 - Unified Model Context Protocol Implementation</p>
        <p className="mt-1">Features: MCP Tools • Context Management • File Operations • Real-time Streaming</p>
      </div>
    </div>
  );
}

export default App;